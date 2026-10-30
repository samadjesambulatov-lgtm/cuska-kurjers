"""Kopīga spēlētāja vārda pārbaude spēlei un API."""

import re

MAX_NAME_LENGTH = 24


def validate_name(value: str) -> str:
    """Noņemt malu atstarpes un pārbaudīt spēlētāja vārdu."""
    name = value.strip()
    if not 1 <= len(name) <= MAX_NAME_LENGTH:
        raise ValueError("Vārdam jābūt no 1 līdz 24 rakstzīmēm.")
    if not re.fullmatch(r"[\w '\-]+", name, flags=re.UNICODE):
        raise ValueError("Lieto burtus, ciparus, atstarpes, _ vai -.")
    return name
