from litestar import Request
from litestar import Response
from litestar import get
from litestar import post
from litestar.datastructures import State
from litestar.params import FromQuery
from litestar.response import Redirect

from server.brave.client import BraveClient
from server.brave.errors import BraveApiError
from server.countries import COUNTRY_CODES
from server.routes.responses import form_value
from server.routes.responses import html
from server.settings_store import SAFESEARCH_CHOICES
from server.settings_store import SettingsStore
from server.views.settings_page import render_settings_page


@get("/settings")
async def settings_page(store: SettingsStore, saved: FromQuery[bool] = False) -> Response[str]:
    notice = "Settings saved." if saved else None
    return html(render_settings_page(store.load(), notice=notice))


@post("/settings/key")
async def update_key(store: SettingsStore, request: Request[None, None, State]) -> Response[str]:
    api_key = await form_value(request, "api_key")
    if not api_key:
        return html(render_settings_page(store.load(), error="Enter an API key."), status_code=400)
    try:
        await BraveClient(api_key=api_key).verify_key()
    except BraveApiError as error:
        return html(render_settings_page(store.load(), error=error.message), status_code=400)
    store.save_api_key(api_key)
    return Redirect(path="/settings?saved=1", status_code=303)


@post("/settings/key/remove")
async def remove_key(store: SettingsStore) -> Response[str]:
    store.clear_api_key()
    return Redirect(path="/setup", status_code=303)


@post("/settings/preferences")
async def update_preferences(store: SettingsStore, request: Request[None, None, State]) -> Response[str]:
    safesearch = await form_value(request, "safesearch")
    country = (await form_value(request, "country")).upper()
    if safesearch not in SAFESEARCH_CHOICES or country not in COUNTRY_CODES:
        return html(render_settings_page(store.load(), error="Those preferences aren't valid."), status_code=400)
    store.save_preferences(safesearch=safesearch, country=country)
    return Redirect(path="/settings?saved=1", status_code=303)
