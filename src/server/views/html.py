import html
import re
from collections.abc import Iterable
from urllib.parse import quote
from urllib.parse import urlsplit

_ALLOWED_MARKUP = re.compile(r"&lt;(/?)(strong|b)&gt;")
_SAFE_SCHEMES = frozenset({"http", "https"})


def escape(text: str) -> str:
    return html.escape(text, quote=True)


def sanitize_markup(markup: str) -> str:
    """Escape API-supplied text but keep the <strong> tags Brave uses to mark matched query terms."""
    return _ALLOWED_MARKUP.sub(r"<\1strong>", escape(markup))


def strip_markup(markup: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", markup))


def safe_url(url: str) -> str:
    """Neutralise javascript:/data: URLs coming back from the API before putting them in an href or src."""
    return url if urlsplit(url).scheme.lower() in _SAFE_SCHEMES else "#"


def query_string(params: Iterable[tuple[str, str]]) -> str:
    encoded = "&".join(f"{quote(key)}={quote(value)}" for key, value in params if value != "")
    return f"?{encoded}" if encoded else ""


def join(parts: Iterable[str]) -> str:
    return "".join(parts)
