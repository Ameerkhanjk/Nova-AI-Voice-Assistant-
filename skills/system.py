"""System skills: time, open apps/folders/URLs, shell commands."""
import subprocess
import sys
import webbrowser
from datetime import datetime


def get_time() -> str:
    return datetime.now().strftime("It's %I:%M %p on %A, %B %d.")


def open_target(target: str) -> str:
    """Open an app, folder, or URL."""
    if target.startswith("http"):
        webbrowser.open(target)
        return f"Opened {target} in your browser."
    opener = {"darwin": "open", "win32": "start", "linux": "xdg-open"}[sys.platform]
    subprocess.Popen(f'{opener} "{target}"', shell=True)
    return f"Opened {target}."


def run_shell(command: str) -> str:
    """Run a shell command and return its output."""
    result = subprocess.run(command, shell=True, capture_output=True,
                            text=True, timeout=30)
    output = (result.stdout or result.stderr).strip()
    return output[:1500] if output else "Command ran with no output."
