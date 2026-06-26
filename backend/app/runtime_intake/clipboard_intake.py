"""Clipboard intake adapter — processes copied Facebook text."""

import sys


def read_clipboard_text() -> str | None:
    """Attempt to read text from system clipboard. Returns None if unavailable."""
    try:
        if sys.platform == "win32":
            import subprocess
            result = subprocess.run(
                ["powershell", "-Command", "Get-Clipboard"],
                capture_output=True, text=True, timeout=5,
            )
            return result.stdout.strip() if result.stdout else None
        elif sys.platform == "darwin":
            import subprocess
            result = subprocess.run(["pbpaste"], capture_output=True, text=True, timeout=5)
            return result.stdout.strip() if result.stdout else None
        else:
            # Linux: requires xclip
            import subprocess
            result = subprocess.run(
                ["xclip", "-selection", "clipboard", "-o"],
                capture_output=True, text=True, timeout=5,
            )
            return result.stdout.strip() if result.stdout else None
    except Exception:
        return None


def clipboard_to_intake_payload(text: str, operator: str = "") -> dict:
    return {
        "capture_method": "clipboard_intake",
        "raw_text": text,
        "operator": operator,
    }
