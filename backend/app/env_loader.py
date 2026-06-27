"""Shared .env loader — one place to load environment for all runtime utilities.

Searches for .env in: project root, backend/, parent directories.
Loads via python-dotenv if found.
Provides sanitized diagnostics (never exposes secrets).
"""

import os
import sys
from pathlib import Path

_loaded = False
_env_path: str | None = None
_env_found: bool = False


def _find_env() -> str | None:
    """Search for .env file in common locations."""
    candidates = [
        Path.cwd() / ".env",                          # current working directory
        Path.cwd() / "backend" / ".env",               # backend/ subdir
        Path(__file__).resolve().parent.parent / ".env",  # project root (backend/..)
        Path(__file__).resolve().parent.parent.parent / ".env",  # above backend/
    ]
    # Also search upward from cwd
    d = Path.cwd()
    for _ in range(3):
        cf = d / ".env"
        if cf not in candidates:
            candidates.append(cf)
        d = d.parent

    for c in candidates:
        if c.exists() and c.is_file():
            return str(c.resolve())
    return None


def load_env(env_file: str | None = None) -> dict:
    """Load .env into os.environ. Returns diagnostics dict (no secrets).

    Call this once at startup in any CLI/utility that needs env vars.
    """
    global _loaded, _env_path, _env_found

    # If caller explicitly provides env_file, always try to load it
    if not env_file and _loaded:
        return _get_diagnostics()

    try:
        from dotenv import load_dotenv
    except ImportError:
        _loaded = True
        return {"env_file_found": False, "error": "python-dotenv not installed"}

    # Use explicit path if given, otherwise search
    if env_file:
        path = Path(env_file)
        if path.exists():
            load_dotenv(path, override=True)  # override to pick up new values
            _env_path = str(path.resolve())
            _env_found = True
            _loaded = True
    elif not _loaded:
        found = _find_env()
        if found:
            load_dotenv(found, override=False)
            _env_path = found
            _env_found = True

    _loaded = True
    return _get_diagnostics()


def _get_diagnostics() -> dict:
    """Return sanitized diagnostics — token values are NEVER exposed."""
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_OPERATOR_CHAT_ID", "")
    test_mode = os.getenv("TELEGRAM_TEST_MODE", "true").lower()

    return {
        "env_file_found": _env_found,
        "env_file_path": _env_path or "not found",
        "telegram_bot_token_present": bool(token and token.strip() and token.strip() != "REPLACE_ME"),
        "telegram_bot_token_masked": _mask(token) if token else "[NOT SET]",
        "telegram_operator_chat_id_present": bool(chat_id and chat_id.strip() and chat_id.strip() != "REPLACE_ME"),
        "telegram_operator_chat_id_masked": _mask(chat_id) if chat_id else "[NOT SET]",
        "telegram_test_mode": test_mode == "true" or test_mode == "1",
        "can_real_send": not (test_mode == "true") and bool(token) and bool(chat_id),
        "loaded": _loaded,
    }


def _mask(value: str) -> str:
    if not value or len(value) < 6:
        return "[NOT SET]"
    if len(value) <= 10:
        return value[:2] + "****" + value[-2:]
    return value[:4] + "****" + value[-4:]


def is_test_mode() -> bool:
    return os.getenv("TELEGRAM_TEST_MODE", "true").lower() in ("true", "1", "yes")


def get_token() -> str:
    return os.getenv("TELEGRAM_BOT_TOKEN", "").strip()


def get_chat_id() -> str:
    return os.getenv("TELEGRAM_OPERATOR_CHAT_ID", "").strip()
