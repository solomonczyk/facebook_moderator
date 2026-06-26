"""Brain loader — loads released brain artifacts for the runtime.

The runtime should use this loader instead of reading raw prompt files.
"""

import os
import json

BRAIN_ROOT = os.path.dirname(os.path.dirname(__file__))


def load_latest_release() -> dict | None:
    """Load the latest brain release metadata."""
    latest_path = os.path.join(BRAIN_ROOT, "BUILD", "releases", "latest.json")
    if not os.path.exists(latest_path):
        return None
    with open(latest_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_release_prompt() -> str | None:
    """Load the latest release SystemPrompt text."""
    meta = load_latest_release()
    if not meta:
        return None
    release_file = meta.get("release_file", "")
    release_path = os.path.join(BRAIN_ROOT, "BUILD", "releases", release_file)
    if not os.path.exists(release_path):
        return None
    with open(release_path, "r", encoding="utf-8") as f:
        return f.read()


def get_loaded_version() -> str:
    """Get the version of the currently loaded brain."""
    meta = load_latest_release()
    return meta.get("brain_version", "unknown") if meta else "none"


def verify_checksum() -> bool:
    """Verify the loaded release checksum matches."""
    from checksum import generate_checksum
    meta = load_latest_release()
    if not meta:
        return False
    prompt = load_release_prompt()
    if not prompt:
        return False
    expected = meta.get("checksum", "")
    actual = generate_checksum(prompt)
    return actual == expected
