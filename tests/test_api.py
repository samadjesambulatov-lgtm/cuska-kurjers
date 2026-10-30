"""REST, datu pārbaudes, saglabāšanas un mājaslapas testi."""

from collections.abc import Generator
from pathlib import Path
from urllib.parse import quote

import pytest
from api.main import create_app
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path: Path) -> Generator[TestClient, None, None]:
    """Katram testam izmantot atsevišķu pagaidu datubāzi."""
    with TestClient(create_app(tmp_path / "test.db")) as session:
        yield session


def test_save_rank_stats_and_pages(client: TestClient) -> None:
    """Saglabāts rezultāts ir redzams topā un spēlētāja profilā."""
    assert client.get("/scores/top").json() == []
    name = "Somats Bečers"
    for score in [20, 60, 40]:
        response = client.post("/scores", json={"name": name, "score": score})
        assert response.status_code == 201
        assert response.json()["created_at"].endswith("Z")
    assert [row["score"] for row in client.get("/scores/top").json()] == [
        60,
        40,
        20,
    ]
    url = "/players/" + quote(name)
    assert client.get(url + "/stats").json() == {
        "name": name,
        "games": 3,
        "best_score": 60,
    }
    assert name in client.get("/").text
    assert client.get(url).status_code == 200
    assert "60 punkti" in client.get(url).text
    assert client.get("/rules").status_code == 200
    assert client.get("/static/style.css").status_code == 200
    assert client.get("/docs").status_code == 200


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"name": "", "score": 10},
        {"name": "  ", "score": 10},
        {"name": "x" * 25, "score": 10},
        {"name": "A", "score": -1},
        {"name": "A", "score": 1.5},
        {"name": "A", "score": "20"},
        {"name": "A", "score": True},
        {"name": "A", "score": 10**30},
        {"name": "<script>", "score": 10},
        {"name": "A/B", "score": 10},
        {"name": "A", "score": 20, "admin": True},
    ],
)
def test_invalid_data_is_not_saved(client: TestClient, payload: dict) -> None:
    """Nederīgi JSON dati dod kļūdu 422 un netiek saglabāti."""
    assert client.post("/scores", json=payload).status_code == 422
    assert client.get("/scores/top").json() == []


def test_missing_body_and_unknown_player(client: TestClient) -> None:
    """Trūkstošiem datiem un nezināmam spēlētājam ir pareizi kodi."""
    assert client.post("/scores").status_code == 422
    assert (
        client.post(
            "/scores",
            content="{",
            headers={"Content-Type": "application/json"},
        ).status_code
        == 422
    )
    assert client.get("/players/unknown/stats").status_code == 404
    assert client.get("/players/unknown").status_code == 404


def test_top_ten_and_tie_order(client: TestClient) -> None:
    """Topā ir līdz desmit spēlēm, vienādos gadījumos pēc ID."""
    for i in range(12):
        client.post("/scores", json={"name": f"Player{i}", "score": i * 20})
    client.post("/scores", json={"name": "Tie", "score": 220})
    rows = client.get("/scores/top").json()
    assert len(rows) == 10
    assert rows[0]["name"] == "Player11" and rows[1]["name"] == "Tie"


def test_database_survives_app_restart(tmp_path: Path) -> None:
    """Jauna lietotne var nolasīt jau saglabātus SQLite rezultātus."""
    path = tmp_path / "scores.db"
    with TestClient(create_app(path)) as client:
        client.post("/scores", json={"name": "Anna", "score": 0})
    with TestClient(create_app(path)) as client:
        assert client.get("/players/Anna/stats").json()["games"] == 1


def test_apostrophes_are_data_and_templates_escape_html(
    client: TestClient,
) -> None:
    """SQL parametri pieņem apostrofus, un Jinja aizsargā tekstu."""
    name = "O'Connor"
    assert (
        client.post("/scores", json={"name": name, "score": 20}).status_code
        == 201
    )
    assert client.get("/players/" + quote(name) + "/stats").status_code == 200
    response = client.get(
        "/players/" + quote("<script>alert(1)</script>", safe="")
    )
    assert "<script>alert(1)</script>" not in response.text
