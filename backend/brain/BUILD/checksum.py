"""SHA256 checksum generation and verification for brain artifacts."""

import hashlib


def generate_checksum(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def verify_checksum(content: str, expected: str) -> bool:
    actual = generate_checksum(content)
    return actual == expected


def checksum_file(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return generate_checksum(f.read())
