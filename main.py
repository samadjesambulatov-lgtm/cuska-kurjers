"""Palaišanas fails: atrod projekta Python vidi un atver spēli."""

import subprocess
from pathlib import Path


def main() -> int:
    """Palaist client/main.py ar Python no projekta .venv mapes."""
    # __file__ ir šis fails; parent ir mape, kurā atrodas viss projekts.
    project = Path(__file__).resolve().parent
    # .venv satur šim projektam uzstādīto Pygame un pārējās bibliotēkas.
    interpreter = project / ".venv" / "Scripts" / "python.exe"
    if not interpreter.is_file():
        print("Vispirms palaid setup.bat, lai uzstādītu projekta bibliotēkas.")
        return 1
    # -m client.main palaiž spēli kā Python moduli, lai darbotos tās importi.
    # cwd nosaka projekta mapi par darba mapi arī tad, ja šo failu palaiž citur.
    return subprocess.call(
        [str(interpreter), "-m", "client.main"], cwd=project
    )


if __name__ == "__main__":
    # Šis bloks izpildās, ja main.py palaiž tieši, nevis importē citā failā.
    raise SystemExit(main())
