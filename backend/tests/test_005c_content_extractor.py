"""Test content extractor: HTML-to-text, Facebook blocks."""

import sys
sys.path.insert(0, '.')

from app.account_worker.content_extractor import (
    extract_text_from_html, extract_facebook_blocks, extract_items,
)


def test_extract_text_strips_tags():
    html = "<div><p>Hello <b>World</b></p></div>"
    text = extract_text_from_html(html)
    assert "Hello World" in text


def test_extract_text_removes_scripts():
    html = "<div>Visible<script>hidden()</script> text</div>"
    text = extract_text_from_html(html)
    assert "Visible" in text
    assert "hidden" not in text


def test_extract_facebook_blocks_finds_usercontent():
    html = '<div class="userContent">Potrebni radnici za branje malina. Kontakt 064-123-4567.</div>'
    blocks = extract_facebook_blocks(html)
    assert len(blocks) > 0
    assert any("Potrebni radnici" in b["text"] for b in blocks)


def test_extract_items_from_blocks():
    blocks = [
        {"text": "Radnici za berbu malina Arilje 064-111-1111", "type": "post"},
        {"text": "Kratko", "type": "comment"},  # Too short, should be skipped
        {"text": "Tražim posao branje malina Subotica", "type": "comment"},
    ]
    items = extract_items(blocks, "https://www.facebook.com/groups/test")
    assert len(items) == 2  # Short one skipped


if __name__ == '__main__':
    test_extract_text_strips_tags()
    test_extract_text_removes_scripts()
    test_extract_facebook_blocks_finds_usercontent()
    test_extract_items_from_blocks()
    print("[PASS] All content extractor tests passed")
