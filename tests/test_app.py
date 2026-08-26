import httpx
from openhost_test_harness import OpenhostStack
from playwright.sync_api import Page
from playwright.sync_api import expect


def test_health_endpoint(stack: OpenhostStack) -> None:
    response = httpx.get(f"{stack.app_url}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_first_boot_prompts_for_an_api_key(stack: OpenhostStack, page: Page) -> None:
    stack.playwright_login(page)
    page.goto(stack.url)
    expect(page).to_have_url(f"{stack.url}/setup")
    expect(page.get_by_role("heading", name="Connect your Brave Search API key")).to_be_visible()
    expect(page.get_by_label("Brave Search API key")).to_be_visible()


def test_app_is_not_reachable_without_owner_auth(stack: OpenhostStack) -> None:
    response = httpx.get(f"{stack.url}/", follow_redirects=False)
    assert response.status_code in (301, 302, 303, 307, 401, 403)
    assert "Connect your Brave Search API key" not in response.text


def test_stylesheet_ships_in_the_image(stack: OpenhostStack) -> None:
    response = httpx.get(f"{stack.app_url}/static/style.css")
    assert response.status_code == 200
    assert ".serp-header" in response.text
