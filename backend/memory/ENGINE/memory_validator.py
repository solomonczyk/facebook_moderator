"""Memory validator — checks data integrity."""

import os
import json

MEMORY_ROOT = os.path.dirname(os.path.dirname(__file__))
DB_DIR = os.path.join(MEMORY_ROOT, "DATABASE")


def validate() -> tuple[bool, list[str]]:
    errors = []

    for domain in ("employers", "workers", "cases", "knowledge"):
        domain_dir = os.path.join(DB_DIR, domain)
        if not os.path.exists(domain_dir):
            continue
        for fname in os.listdir(domain_dir):
            if not fname.endswith(".json"):
                continue
            path = os.path.join(domain_dir, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                errors.append(f"Invalid JSON: {domain}/{fname}")
                continue

            eid = data.get(f"{domain.rstrip('s')}_id") or data.get("entry_id") or data.get("case_id")
            if not eid:
                errors.append(f"Missing ID: {domain}/{fname}")

            ts = data.get("created_at")
            if not ts:
                errors.append(f"Missing timestamp: {domain}/{fname}")

            if domain in ("employers", "workers"):
                trust = data.get("trust_score")
                if trust is not None and not (0.0 <= trust <= 1.0):
                    errors.append(f"Invalid trust score: {domain}/{fname}")

    return len(errors) == 0, errors


if __name__ == "__main__":
    ok, errors = validate()
    if ok:
        print("PASS")
    else:
        print("FAIL")
        for e in errors:
            print(f"  {e}")
