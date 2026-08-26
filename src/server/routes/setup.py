from litestar import Request
from litestar import Response
from litestar import get
from litestar import post
from litestar.datastructures import State
from litestar.response import Redirect

from server.brave.client import BraveClient
from server.brave.errors import BraveApiError
from server.routes.responses import form_value
from server.routes.responses import html
from server.settings_store import SettingsStore
from server.views.setup_page import render_setup_page


@get("/setup")
async def setup_page(store: SettingsStore) -> Response[str]:
    if store.load().is_configured:
        return Redirect(path="/", status_code=303)
    return html(render_setup_page())


@post("/setup")
async def submit_setup(store: SettingsStore, request: Request[None, None, State]) -> Response[str]:
    api_key = await form_value(request, "api_key")
    if not api_key:
        return html(render_setup_page(error="Enter an API key."), status_code=400)
    try:
        await BraveClient(api_key=api_key).verify_key()
    except BraveApiError as error:
        return html(render_setup_page(error=error.message), status_code=400)
    store.save_api_key(api_key)
    return Redirect(path="/", status_code=303)
