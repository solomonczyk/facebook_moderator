#!/usr/bin/env python3
"""Brain validator — verifies all source documents exist and are valid."""

import os
import sys
from dataclasses import dataclass, field

BRAIN_ROOT = os.path.dirname(os.path.dirname(__file__))


@dataclass
class ValidationResult:
    passed: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def fail(self, msg: str) -> None:
        self.passed = False
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def validate() -> ValidationResult:
    result = ValidationResult()

    # Import manifest (avoid yaml dependency by using fallback)
    sys.path.insert(0, os.path.dirname(__file__))
    from manifest import load_manifest, get_all_source_files

    manifest = load_manifest()
    brain = manifest.get("brain", {})

    # 1. Required sections exist
    required_sections = ["constitution", "policies", "knowledge", "prompts"]
    for section in required_sections:
        if section not in brain:
            result.fail(f"Missing manifest section: {section}")

    # 2. All source files exist
    for rel_path in get_all_source_files():
        abs_path = os.path.join(BRAIN_ROOT, rel_path)
        if not os.path.exists(abs_path):
            result.fail(f"Missing source file: {rel_path}")

    # 3. No empty documents
    for rel_path in get_all_source_files():
        abs_path = os.path.join(BRAIN_ROOT, rel_path)
        if os.path.exists(abs_path):
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if len(content) < 50:
                result.fail(f"Document too short (<50 chars): {rel_path}")

    # 4. Constitution exists
    const_files = brain.get("constitution", [])
    if not const_files:
        result.fail("No constitution documents in manifest")

    # 5. Version is valid
    version = brain.get("version", "")
    if not version:
        result.fail("No version in manifest")
    parts = str(version).split(".")
    if len(parts) != 3:
        result.fail(f"Invalid version format: {version}")

    # 6. Few-shot examples exist
    prompt_files = brain.get("prompts", [])
    has_fewshot = any("FewShot" in f for f in prompt_files)
    if not has_fewshot:
        result.fail("No FewShot.md in prompts")

    # 7. Negative examples exist
    has_negative = any("Negative" in f for f in prompt_files)
    if not has_negative:
        result.warn("No NegativeExamples.md in prompts")

    # 8. JSON contract exists
    has_json = any("JsonContract" in f for f in prompt_files)
    if not has_json:
        result.fail("No JsonContract.md in prompts")

    # 9. Safety model exists
    policy_files = brain.get("policies", [])
    has_safety = any("SAFETY" in f for f in policy_files)
    if not has_safety:
        result.fail("No safety model in policies")

    # 10. Check for duplicate section names across all files
    all_headers = []
    for rel_path in get_all_source_files():
        abs_path = os.path.join(BRAIN_ROOT, rel_path)
        if os.path.exists(abs_path):
            with open(abs_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("## "):
                        all_headers.append(line.strip())

    from collections import Counter
    dupes = [h for h, c in Counter(all_headers).items() if c > 1]
    if dupes:
        result.warn(f"Duplicate section headers: {dupes[:5]}")

    return result


if __name__ == "__main__":
    result = validate()
    if result.passed:
        print("PASS")
    else:
        print("FAIL")
        for e in result.errors:
            print(f"  ERROR: {e}")
    for w in result.warnings:
        print(f"  WARN: {w}")
    sys.exit(0 if result.passed else 1)
