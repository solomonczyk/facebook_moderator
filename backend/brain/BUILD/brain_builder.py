#!/usr/bin/env python3
"""Brain Builder — assembles source documents into a single SystemPrompt.md release."""

import os
import sys
import json
from datetime import datetime, timezone

BRAIN_ROOT = os.path.dirname(os.path.dirname(__file__))
BUILD_DIR = os.path.dirname(__file__)


def build() -> dict:
    """Build the brain release. Returns build metadata dict."""
    sys.path.insert(0, BUILD_DIR)
    from manifest import load_manifest, get_all_source_files, get_version
    from checksum import generate_checksum

    manifest = load_manifest()
    brain = manifest.get("brain", {})
    version = get_version()
    output_cfg = manifest.get("output", {})

    # Collect all source content
    sections = []
    source_files_used = []

    # Header with version
    header = f"# System Prompt — FB Group Runtime Manager v{version}\n\n"
    header += f"Build: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
    header += f"Version: {version}\n\n"
    header += "## Table of Contents\n\n"

    toc_entries = []

    # Process each section
    section_map = [
        ("constitution", "## Constitution"),
        ("policies", "## Policies"),
        ("knowledge", "## Knowledge"),
        ("prompts", "## Prompt Resources"),
    ]

    content_blocks = [header]

    for section_key, section_title in section_map:
        files = brain.get(section_key, [])
        if not files:
            continue

        content_blocks.append(f"\n{section_title}\n")
        toc_entries.append(f"- {section_title.strip('# ')}")

        for rel_path in files:
            abs_path = os.path.join(BRAIN_ROOT, rel_path)
            if os.path.exists(abs_path):
                with open(abs_path, "r", encoding="utf-8") as f:
                    doc_content = f.read()

                # Remove the document's own H1 title (first # line) to avoid duplication
                lines = doc_content.split("\n")
                if lines and lines[0].startswith("# "):
                    lines = lines[1:]
                doc_content = "\n".join(lines).strip()

                # Extract H2 headers for TOC
                for line in lines:
                    if line.startswith("## "):
                        toc_entries.append(f"  - {line.strip('# ').strip()}")

                content_blocks.append(f"\n{doc_content}\n")
                source_files_used.append(rel_path)

    # Insert TOC after header
    toc_text = "\n".join(toc_entries) + "\n"
    content_blocks.insert(1, toc_text)

    # Add source manifest at the end
    content_blocks.append("\n---\n## Source Documents\n")
    for f in source_files_used:
        content_blocks.append(f"- {f}")
    content_blocks.append(f"\n*Brain v{version} — built {datetime.now(timezone.utc).strftime('%Y-%m-%d')}*")

    full_content = "\n".join(content_blocks)
    checksum = generate_checksum(full_content)

    # Write SystemPrompt.md
    output_path = os.path.join(BRAIN_ROOT, output_cfg.get("system_prompt", "PROMPTS/SystemPrompt.md"))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_content)

    # Write release
    release_dir = os.path.join(BRAIN_ROOT, output_cfg.get("release_dir", "BUILD/releases"))
    os.makedirs(release_dir, exist_ok=True)

    release_md = os.path.join(release_dir, f"brain-{version}.md")
    with open(release_md, "w", encoding="utf-8") as f:
        f.write(full_content)

    # Write release JSON
    release_json = os.path.join(release_dir, f"brain-{version}.json")
    with open(release_json, "w", encoding="utf-8") as f:
        json.dump({
            "brain_version": version,
            "build": 1,
            "release": "stable",
            "checksum": checksum,
            "built_at": datetime.now(timezone.utc).isoformat(),
            "source_files": source_files_used,
            "source_count": len(source_files_used),
        }, f, indent=2)

    # Write latest.json
    latest_json = os.path.join(BRAIN_ROOT, output_cfg.get("latest_json", "BUILD/releases/latest.json"))
    os.makedirs(os.path.dirname(latest_json), exist_ok=True)
    with open(latest_json, "w", encoding="utf-8") as f:
        json.dump({
            "brain_version": version,
            "status": "stable",
            "release_file": f"brain-{version}.md",
            "release_json": f"brain-{version}.json",
            "checksum": checksum,
            "built_at": datetime.now(timezone.utc).isoformat(),
        }, f, indent=2)

    return {
        "version": version,
        "checksum": checksum,
        "source_files": len(source_files_used),
        "output": release_md,
        "release_json": release_json,
        "latest_json": latest_json,
    }


if __name__ == "__main__":
    result = build()
    print("Brain Build Successful\n")
    print(f"Version:  {result['version']}")
    print(f"Checksum: {result['checksum'][:16]}...")
    print(f"Sources:  {result['source_files']} files")
    print(f"Output:   {result['output']}")
    print(f"Release:  {result['release_json']}")
