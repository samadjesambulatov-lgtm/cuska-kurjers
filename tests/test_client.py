"""Saziņas kļūdu apstrādes testi bez Pygame loga."""

from unittest.mock import patch

import requests
from client.api_client import ApiClient


def test_disconnected_server_does_not_raise() -> None:
    """Abas saziņas kļūdas pārvēršas par parādāmiem paziņojumiem."""
    client = ApiClient("http://127.0.0.1:1")
    with patch("requests.get", side_effect=requests.ConnectionError):
        assert not client.load_top().ok
    with patch("requests.post", side_effect=requests.Timeout):
        assert not client.save_score("Anna", 20).ok


def test_malformed_ranking_does_not_raise() -> None:
    """Negaidīta servera atbilde nepārtrauc izvēlnes zīmēšanu."""
    with patch("requests.get") as request:
        request.return_value.json.return_value = [{"unexpected": 1}]
        assert not ApiClient().load_top().ok
