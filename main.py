"""Spēles palaišana ar projektā uzstādītajām bibliotēkām."""

import subprocess
from pathlib import Path


def main() -> int:
    """Palaist Pygame klientu projekta virtuālajā vidē."""
    project = Path(__file__).resolve().parent
    interpreter = project / ".venv" / "Scripts" / "python.exe"
    if not interpreter.is_file():
        print("Vispirms palaid setup.bat, lai uzstādītu projekta bibliotēkas.")
        return 1
    return subprocess.call(
        [str(interpreter), "-m", "client.main"], cwd=project
    )


if __name__ == "__main__":
    raise SystemExit(main())
