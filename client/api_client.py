"""Spēles saziņa ar serveri: rezultātu ielāde un nosūtīšana.

Šīs metodes fonā izsauc client/main.py, lai servera gaidīšana neapturētu logu.
"""

import os
from dataclasses import dataclass

import requests


@dataclass
class ApiResult:
    """Pieprasījuma iznākums: vai izdevās, ko parādīt un kādi dati saņemti."""

    ok: bool
    message: str
    scores: list[dict] | None = None


class ApiClient:
    """Ielādēt labākos rezultātus un nosūtīt pabeigto spēli."""

    def __init__(self, base_url: str | None = None) -> None:
        """Izmantot vietējo serveri vai norādīto SPELE_API_URL adresi."""
        # Vispirms izmantojam padoto adresi. Ja tās nav, lasām SPELE_API_URL.
        # Ja arī tas nav iestatīts, izmantojam serveri šajā datorā uz porta 8000.
        self.base_url = (
            base_url or os.getenv("SPELE_API_URL", "http://127.0.0.1:8000")
        ).rstrip("/")

    def load_top(self) -> ApiResult:
        """Ar GET pieprasījumu saņemt servera labāko rezultātu sarakstu."""
        try:
            # GET nolasa datus. timeout=(1.5, 3) ierobežo savienojuma
            # izveides gaidīšanu līdz 1,5 s un atbildes datu gaidīšanu līdz 3 s.
            response = requests.get(
                f"{self.base_url}/scores/top", timeout=(1.5, 3)
            )
            # Ja serveris atbild ar kļūdas kodu, pārejam uz except bloku.
            response.raise_for_status()
            scores = response.json()
            # Sagaidām sarakstu; katrā rindā vajag name tekstu un score skaitli.
            # Nepareiza atbilde nedrīkst izraisīt spēles avāriju.
            if not isinstance(scores, list) or any(
                not isinstance(row, dict)
                or not isinstance(row.get("name"), str)
                or not isinstance(row.get("score"), int)
                for row in scores
            ):
                raise ValueError("Negaidīts rezultātu atbildes formāts")
            return ApiResult(True, "Serveris pieejams.", scores[:10])
        except (requests.RequestException, ValueError):
            # Saziņas vai datu kļūdu pārvēršam paziņojumā spēles logam.
            return ApiResult(
                False, "Serveris nav pieejams. Spēlēt var arī bez tā."
            )

    def save_score(self, name: str, score: int) -> ApiResult:
        """Ar POST nosūtīt spēlētāja vārdu un pabeigtās partijas punktus."""
        # Neatkārtojam POST automātiski: serveris var jau būt saglabājis rezultātu,
        # pat ja atbilde pazudusi. Atkārtojums varētu izveidot otru tādu pašu ierakstu.
        try:
            response = requests.post(
                f"{self.base_url}/scores",
                json={"name": name, "score": score},
                timeout=(1.5, 3),
            )
            response.raise_for_status()
            # 201 nozīmē, ka serverī ir izveidots jauns rezultāta ieraksts.
            if response.status_code != 201:
                return ApiResult(False, "Serveris neapstiprināja saglabāšanu.")
            return ApiResult(True, "Rezultāts saglabāts serverī.")
        except requests.RequestException:
            return ApiResult(
                False, "Savienojuma kļūda: rezultāts nav apstiprināts."
            )
