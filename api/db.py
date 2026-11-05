"""Rezultātu saglabāšana SQLite failā un to nolasīšana serverim.

Šeit ir SQL komandas. API adreses un HTML lapas atrodas api/main.py.
"""

import sqlite3
from contextlib import closing
from pathlib import Path


class Database:
    """Darbības ar rezultātu datubāzi: saglabāt, nolasīt topu un statistiku."""

    def __init__(self, path: str | Path) -> None:
        """Saglabāt datubāzes ceļu, vēl neatverot savienojumu."""
        self.path = Path(path)

    def connect(self) -> sqlite3.Connection:
        """Atvērt savienojumu ar SQLite datubāzes failu."""
        connection = sqlite3.connect(self.path, timeout=5)
        # sqlite3.Row ļauj rakstīt row["score"], nevis minēt kolonnas numuru.
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        """Izveidot datu mapi un tabulu, ja tās vēl neeksistē."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # connection saglabā izmaiņas, ja nav kļūdas; kļūdas gadījumā tās atceļ.
        # closing pēc šī bloka vienmēr aizver datubāzes savienojumu.
        with closing(self.connect()) as connection, connection:
            # Katra rinda ir viena pabeigta spēle. id piešķir automātiski,
            # created_at saglabā servera UTC laiku. Esošos rezultātus nedzēšam.
            connection.execute("""
                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    score INTEGER NOT NULL CHECK(score >= 0),
                    created_at TEXT NOT NULL DEFAULT
                        (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
                )
            """)
            # Indekss palīdz ātrāk atrast labākos rezultātus, kad ierakstu ir daudz.
            connection.execute("""
                CREATE INDEX IF NOT EXISTS score_ranking
                ON scores(score DESC, id ASC)
            """)

    def add_score(self, name: str, score: int) -> dict:
        """Pievienot rezultātu un atgriezt tā identifikatoru un laiku."""
        with closing(self.connect()) as connection, connection:
            # ? vietā SQLite droši ievieto name un score kā datus.
            # Spēlētāja vārds tā nevar kļūt par izpildāmu SQL komandu.
            cursor = connection.execute(
                "INSERT INTO scores(name, score) VALUES (?, ?)",
                (name, score),
            )
            # lastrowid ir tikko pievienotās rindas ID. Nolasām arī tās UTC laiku.
            row = connection.execute(
                "SELECT * FROM scores WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
            return dict(row)

    def top_scores(self) -> list[dict]:
        """Nolasīt līdz 10 labākajām partijām, sākot ar lielāko punktu skaitu."""
        with closing(self.connect()) as connection:
            rows = connection.execute(
                # DESC = no lielākā uz mazāko. Pie vienādiem punktiem mazāks ID
                # ir augstāk — tas nozīmē agrāk saglabātu rezultātu. LIMIT ir 10.
                "SELECT * FROM scores ORDER BY score DESC, id ASC LIMIT 10"
            ).fetchall()
            return [dict(row) for row in rows]

    def player_stats(self, name: str) -> dict | None:
        """Atgriezt spēļu skaitu un rekordu vai None nezināmam vārdam."""
        with closing(self.connect()) as connection:
            # WHERE atlasa šī vārda spēles; COUNT tās saskaita,
            # bet MAX atrod lielāko punktu skaitu.
            row = connection.execute(
                "SELECT COUNT(*) AS games, MAX(score) AS best_score "
                "FROM scores WHERE name = ?",
                (name,),
            ).fetchone()
            # Ja spēļu skaits ir 0, šādam vārdam nav saglabāta rezultāta.
            if row["games"] == 0:
                return None
            return {"name": name, **dict(row)}
