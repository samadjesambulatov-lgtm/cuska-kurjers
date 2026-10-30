"""Vienkārša SQLite datubāze ar parametrizētiem vaicājumiem."""

import sqlite3
from contextlib import closing
from pathlib import Path


class Database:
    """Atvērt datubāzes savienojumus rezultātiem un statistikai."""

    def __init__(self, path: str | Path) -> None:
        """Saglabāt datubāzes ceļu, vēl neatverot savienojumu."""
        self.path = Path(path)

    def connect(self) -> sqlite3.Connection:
        """Atgriezt savienojumu ar piekļuvi kolonnām pēc nosaukuma."""
        connection = sqlite3.connect(self.path, timeout=5)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        """Izveidot trūkstošo datu mapi, tabulu un rezultātu indeksu."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self.connect()) as connection, connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    score INTEGER NOT NULL CHECK(score >= 0),
                    created_at TEXT NOT NULL DEFAULT
                        (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
                )
            """)
            connection.execute("""
                CREATE INDEX IF NOT EXISTS score_ranking
                ON scores(score DESC, id ASC)
            """)

    def add_score(self, name: str, score: int) -> dict:
        """Pievienot rezultātu un atgriezt tā identifikatoru un laiku."""
        with closing(self.connect()) as connection, connection:
            cursor = connection.execute(
                "INSERT INTO scores(name, score) VALUES (?, ?)",
                (name, score),
            )
            row = connection.execute(
                "SELECT * FROM scores WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
            return dict(row)

    def top_scores(self) -> list[dict]:
        """Atgriezt desmit labākās spēles, vienādos gadījumos pēc laika."""
        with closing(self.connect()) as connection:
            rows = connection.execute(
                "SELECT * FROM scores ORDER BY score DESC, id ASC LIMIT 10"
            ).fetchall()
            return [dict(row) for row in rows]

    def player_stats(self, name: str) -> dict | None:
        """Atgriezt spēļu skaitu un rekordu vai None nezināmam vārdam."""
        with closing(self.connect()) as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS games, MAX(score) AS best_score "
                "FROM scores WHERE name = ?",
                (name,),
            ).fetchone()
            if row["games"] == 0:
                return None
            return {"name": name, **dict(row)}
