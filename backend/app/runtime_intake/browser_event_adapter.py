"""Browser event adapter: validates and transforms browser extension payloads."""


def validate_browser_payload(data: dict) -> list[str]:
    errors = []
    if not data.get("selected_text", "").strip():
        errors.append("selected_text is required and cannot be empty")
    if len(data.get("selected_text", "")) > 10000:
        errors.append("selected_text exceeds 10000 character limit")
    return errors


def adapt_browser_payload(data: dict) -> dict:
    """Normalize browser extension payload for intake."""
    return {
        "capture_method": data.get("capture_method", "browser_extension_visible_selection"),
        "page_url": data.get("page_url", ""),
        "page_title": data.get("page_title", ""),
        "selected_text": data.get("selected_text", "").strip(),
        "source_group": data.get("source_group", ""),
        "captured_at": data.get("captured_at", ""),
        "operator": data.get("operator", ""),
    }
