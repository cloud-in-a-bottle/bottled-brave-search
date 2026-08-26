from litestar import Litestar
from litestar.testing import TestClient

from server.settings_store import SettingsStore
from tests.brave_stub import VALID_KEY


def test_unconfigured_app_redirects_to_setup(client: TestClient[Litestar]) -> None:
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/setup"


def test_setup_page_explains_how_to_get_a_key(client: TestClient[Litestar]) -> None:
    body = client.get("/setup").text
    assert "Connect your Brave Search API key" in body
    assert "https://api-dashboard.search.brave.com/register" in body
    assert "https://api-dashboard.search.brave.com/app/keys" in body


def test_rejected_key_is_not_stored(client: TestClient[Litestar], store: SettingsStore) -> None:
    response = client.post("/setup", data={"api_key": "not-a-real-key"}, follow_redirects=False)
    assert response.status_code == 400
    assert "The provided subscription token is invalid." in response.text
    assert store.load().brave_api_key is None


def test_rejected_key_is_echoed_back_so_the_submit_does_not_look_like_a_no_op(
    client: TestClient[Litestar],
) -> None:
    response = client.post("/setup", data={"api_key": "not-a-real-key"}, follow_redirects=False)
    assert 'value="not-a-real-key"' in response.text
    assert response.headers["cache-control"] == "no-store"


def test_empty_submission_says_so(client: TestClient[Litestar]) -> None:
    response = client.post("/setup", data={"api_key": "  "}, follow_redirects=False)
    assert response.status_code == 400
    assert "Enter an API key." in response.text


def test_accepted_key_is_stored_and_unlocks_the_app(client: TestClient[Litestar], store: SettingsStore) -> None:
    response = client.post("/setup", data={"api_key": VALID_KEY}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert store.load().brave_api_key == VALID_KEY
    assert "Brave Search" in client.get("/").text


def test_key_is_masked_on_the_settings_page(configured_client: TestClient[Litestar]) -> None:
    body = configured_client.get("/settings").text
    assert VALID_KEY not in body
    assert "BSA-" in body


def test_removing_the_key_sends_the_owner_back_to_setup(
    configured_client: TestClient[Litestar], store: SettingsStore
) -> None:
    response = configured_client.post("/settings/key/remove", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/setup"
    assert store.load().brave_api_key is None


def test_preferences_are_persisted(configured_client: TestClient[Litestar], store: SettingsStore) -> None:
    response = configured_client.post(
        "/settings/preferences", data={"safesearch": "off", "country": "GB"}, follow_redirects=False
    )
    assert response.status_code == 303
    settings = store.load()
    assert settings.safesearch == "off"
    assert settings.country == "GB"


def test_invalid_preferences_are_rejected(configured_client: TestClient[Litestar], store: SettingsStore) -> None:
    response = configured_client.post(
        "/settings/preferences", data={"safesearch": "nonsense", "country": "GB"}, follow_redirects=False
    )
    assert response.status_code == 400
    assert store.load().safesearch == "moderate"
