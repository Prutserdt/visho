"""Opening the result in the default browser (Linux, Windows, macOS)."""

import subprocess
import sys
import webbrowser
from pathlib import Path


def open_in_browser(path: Path) -> None:
    path = path.resolve()
    if sys.platform.startswith("linux"):
        try:
            subprocess.Popen(
                ["xdg-open", str(path)],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return
        except FileNotFoundError:
            pass
    if not webbrowser.open(path.as_uri()):
        print(f"\nOpen this file manually:\n  {path}")
