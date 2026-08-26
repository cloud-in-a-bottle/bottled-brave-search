from litestar import Litestar
from litestar.testing import TestClient

from server.settings_store import SettingsStore


def test_web_results_render_google_style_blocks(configured_client: TestClient[Litestar]) -> None:
    body = configured_client.get("/search", params={"q": "otters"}).text
    assert "Otter - Wikipedia" in body
    assert "en.wikipedia.org › wiki › Otter" in body
    # The feature blocks Google interleaves into the result column.
    assert "Top stories" in body
    assert "People also ask" in body
    assert "Discussions and forums" in body
    # The knowledge panel.
    assert "kp-title" in body
    assert "Lutrinae" in body


def test_web_results_keep_bold_match_markup_but_escape_everything_else(
    configured_client: TestClient[Litestar],
) -> None:
    body = configured_client.get("/search", params={"q": "otters"}).text
    assert "<strong>otters</strong>" in body
    assert "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;" in body
    assert "<script>alert('xss')</script>" not in body
    assert "<img src=x onerror=alert(1)>" not in body


def test_pager_links_to_the_next_page(configured_client: TestClient[Litestar]) -> None:
    body = configured_client.get("/search", params={"q": "otters"}).text
    assert "pager" in body
    assert "start=10" in body


def test_second_page_requests_the_next_brave_offset(configured_client: TestClient[Litestar]) -> None:
    body = configured_client.get("/search", params={"q": "otters", "start": "10"}).text
    assert 'class="pager-cell pager-current"' in body
    assert "Previous" in body


def test_images_tab_renders_a_justified_grid(configured_client: TestClient[Litestar]) -> None:
    body = configured_client.get("/search", params={"q": "otters", "tab": "images"}).text
    assert "image-grid" in body
    assert body.count('class="image-tile"') == 40
    assert "flex-grow:" in body


def test_news_tab_renders_articles(configured_client: TestClient[Litestar]) -> None:
    body = configured_client.get("/search", params={"q": "otters", "tab": "news"}).text
    assert "news-item" in body
    assert "Breaking" in body
    assert "Otter story number 1" in body


def test_tabs_preserve_the_query(configured_client: TestClient[Litestar]) -> None:
    body = configured_client.get("/search", params={"q": "otters"}).text
    assert "/search?q=otters&amp;tab=images" in body
    assert "/search?q=otters&amp;tab=news" in body


def test_time_filter_is_offered_and_marked_active(configured_client: TestClient[Litestar]) -> None:
    body = configured_client.get("/search", params={"q": "otters", "freshness": "pw"}).text
    assert "Past week" in body
    assert 'class="tool-option active"' in body


def test_empty_query_returns_to_the_home_page(configured_client: TestClient[Litestar]) -> None:
    response = configured_client.get("/search", params={"q": "   "}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_search_without_a_key_goes_to_setup(client: TestClient[Litestar]) -> None:
    response = client.get("/search", params={"q": "otters"}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/setup"


def test_upstream_failure_is_shown_as_a_search_error(client: TestClient[Litestar], store: SettingsStore) -> None:
    store.save_api_key("a-key-the-stub-rejects")
    response = client.get("/search", params={"q": "otters"})
    assert response.status_code == 502
    assert "That search didn't go through" in response.text
    assert "Update your API key in Settings" in response.text


def test_feeling_lucky_jumps_to_the_first_result(configured_client: TestClient[Litestar]) -> None:
    response = configured_client.get("/lucky", params={"q": "otters"}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "https://en.wikipedia.org/wiki/Otter"
