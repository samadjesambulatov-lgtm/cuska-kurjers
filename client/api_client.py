"""HTTP pieprasījumi Pygame lietotnes fona pavedienos."""

import os
from dataclasses import dataclass

import requests


@dataclass
class ApiResult:
    """Servera atbilde, kuru var parādīt, neapturot spēli."""

    ok: bool
    message: str
    scores: list[dict] | None = None


class ApiClient:
    """Ielādēt labākos rezultātus un nosūtīt pabeigto spēli."""

    def __init__(self, base_url: str | None = None) -> None:
        """Izmantot vietējo serveri vai norādīto SPELE_API_URL adresi."""
        self.base_url = (
            base_url or os.getenv("SPELE_API_URL", "http://127.0.0.1:8000")
        ).rstrip("/")

    def load_top(self) -> ApiResult:
        """Ielādēt desmit rezultātus vai paziņot par saziņas kļūdu."""
        try:
            response = requests.get(
                f"{self.base_url}/scores/top", timeout=(1.5, 3)
            )
            response.raise_for_status()
            scores = response.json()
            if not isinstance(scores, list) or any(
                not isinstance(row, dict)
                or not isinstance(row.get("name"), str)
                or not isinstance(row.get("score"), int)
                for row in scores
            ):
                raise ValueError("Negaidīts rezultātu atbildes formāts")
            return ApiResult(True, "Serveris pieejams.", scores[:10])
        except (requests.RequestException, ValueError):
            return ApiResult(
                False, "Serveris nav pieejams. Spēlēt var arī bez tā."
            )

    def save_score(self, name: str, score: int) -> ApiResult:
        """Nosūtīt rezultātu vienu reizi, neveidojot dublikātus."""
        try:
            response = requests.post(
                f"{self.base_url}/scores",
                json={"name": name, "score": score},
                timeout=(1.5, 3),
            )
            response.raise_for_status()
            if response.status_code != 201:
                return ApiResult(False, "Serveris neapstiprināja saglabāšanu.")
            return ApiResult(True, "Rezultāts saglabāts serverī.")
        except requests.RequestException:
            return ApiResult(
                False, "Savienojuma kļūda: rezultāts nav apstiprināts."
            )
