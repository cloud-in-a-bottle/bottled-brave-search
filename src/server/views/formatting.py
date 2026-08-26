from datetime import datetime


def format_result_date(page_age: str | None, age: str | None) -> str | None:
    """Google shows an absolute date ("Jan 5, 2024") before the snippet; Brave gives an ISO stamp or a phrase."""
    if page_age is not None:
        parsed = _parse_iso(page_age)
        if parsed is not None:
            return f"{parsed:%b} {parsed.day}, {parsed.year}"
    return age


def _parse_iso(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def format_seconds(seconds: float) -> str:
    return f"{seconds:.2f}"
