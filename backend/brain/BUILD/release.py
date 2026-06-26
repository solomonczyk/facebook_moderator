"""Brain release manager — manages versioned brain releases."""

import os
import json
import shutil
from datetime import datetime, timezone

BRAIN_ROOT = os.path.dirname(os.path.dirname(__file__))
RELEASE_DIR = os.path.join(BRAIN_ROOT, "BUILD", "releases")


def list_releases() -> list[dict]:
    """List all available brain releases."""
    releases = []
    if not os.path.exists(RELEASE_DIR):
        return releases
    for f in sorted(os.listdir(RELEASE_DIR)):
        if f.startswith("brain-") and f.endswith(".json") and f != "latest.json":
            path = os.path.join(RELEASE_DIR, f)
            with open(path, "r", encoding="utf-8") as fh:
                releases.append(json.load(fh))
    return releases


def get_latest_release() -> dict | None:
    """Get the latest release metadata."""
    latest_path = os.path.join(RELEASE_DIR, "latest.json")
    if not os.path.exists(latest_path):
        return None
    with open(latest_path, "r", encoding="utf-8") as f:
        return json.load(f)


def archive_old_releases(keep: int = 5) -> int:
    """Archive old releases, keeping the N most recent. Returns count archived."""
    releases = list_releases()
    if len(releases) <= keep:
        return 0
    archived = 0
    archive_dir = os.path.join(RELEASE_DIR, "archive")
    os.makedirs(archive_dir, exist_ok=True)
    for release in releases[:-keep]:
        version = release.get("brain_version", "unknown")
        for ext in (".md", ".json"):
            src = os.path.join(RELEASE_DIR, f"brain-{version}{ext}")
            if os.path.exists(src):
                dst = os.path.join(archive_dir, f"brain-{version}{ext}")
                shutil.move(src, dst)
        archived += 1
    return archived
