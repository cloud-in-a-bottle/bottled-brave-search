import pytest

from server.views.html import safe_url
from server.views.html import sanitize_markup


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://example.test/a", "https://example.test/a"),
        ("http://example.test/a", "http://example.test/a"),
        ("javascript:alert(1)", "#"),
        ("JavaScript:alert(1)", "#"),
        ("data:text/html;base64,PHNjcmlwdD4=", "#"),
    ],
)
def test_only_http_urls_survive(url: str, expected: str) -> None:
    assert safe_url(url) == expected


def test_sanitize_keeps_bold_and_escapes_the_rest() -> None:
    assert sanitize_markup("a <strong>b</strong> <em onclick='x'>c</em>") == (
        "a <strong>b</strong> &lt;em onclick=&#x27;x&#x27;&gt;c&lt;/em&gt;"
    )
