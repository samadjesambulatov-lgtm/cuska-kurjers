"""Vienādi spēlētāja vārda noteikumi spēles izvēlnei un serverim."""

import re

MAX_NAME_LENGTH = 24


def validate_name(value: str) -> str:
    """Atgriezt derīgu vārdu vai ar ValueError paziņot par kļūdu."""
    # strip noņem atstarpes sākumā un beigās, bet atstāj atstarpes starp vārdiem.
    name = value.strip()
    if not 1 <= len(name) <= MAX_NAME_LENGTH:
        raise ValueError("Vārdam jābūt no 1 līdz 24 rakstzīmēm.")
    # \w atļauj burtus (arī ā, č, ē), ciparus un _. Papildus atļaujam
    # atstarpi, apostrofu un defisi. fullmatch pārbauda visu ievadīto vārdu.
    if not re.fullmatch(r"[\w '\-]+", name, flags=re.UNICODE):
        raise ValueError("Lieto burtus, ciparus, atstarpes, _ vai -.")
    return name
