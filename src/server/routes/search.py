import time
from urllib.parse import quote

from litestar import Response
from litestar import get
from litestar.params import FromQuery
from litestar.response import Redirect

from server.brave.client import BraveClient
from server.brave.errors import BraveApiError
from server.routes.responses import html
from server.search_params import IMAGE_RESULT_COUNT
from server.search_params import RESULTS_PER_PAGE
from server.search_params import SearchParams
from server.search_params import Tab
from server.search_params import parse_search_params
from server.settings_store import AppSettings
from server.settings_store import SettingsStore
from server.views.error_page import render_search_error
from server.views.home import render_home_page
from server.views.home import render_lucky_not_found
from server.views.html import safe_url
from server.views.image_results import render_image_results
from server.views.layout import render_document
from server.views.layout import render_footer
from server.views.layout import render_search_header
from server.views.news_results import render_news_results
from server.views.web_results import render_web_results


@get("/")
async def index(store: SettingsStore) -> Response[str]:
    if not store.load().is_configured:
        return Redirect(path="/setup", status_code=303)
    return html(render_home_page())


@get("/search")
async def search(
    store: SettingsStore,
    q: FromQuery[str] = "",
    tab: FromQuery[str] = "all",
    start: FromQuery[str] = "0",
    freshness: FromQuery[str] = "",
    spellcheck: FromQuery[str] = "1",
) -> Response[str]:
    settings = store.load()
    if settings.brave_api_key is None:
        return Redirect(path="/setup", status_code=303)
    params = parse_search_params(query=q, tab=tab, start=start, freshness=freshness, spellcheck=spellcheck)
    if not params.query:
        return Redirect(path="/", status_code=303)

    client = BraveClient(api_key=settings.brave_api_key)
    try:
        results_html = await _run_search(client, params, settings)
    except BraveApiError as error:
        return html(render_search_error(params, error), status_code=502)

    body = render_search_header(params) + results_html + render_footer()
    return html(render_document(f"{params.query} - Brave Search", body, body_class="serp-page"))


@get("/lucky")
async def lucky(store: SettingsStore, q: FromQuery[str] = "") -> Response[str]:
    settings = store.load()
    if settings.brave_api_key is None:
        return Redirect(path="/setup", status_code=303)
    query = q.strip()
    if not query:
        return Redirect(path="/", status_code=303)

    client = BraveClient(api_key=settings.brave_api_key)
    try:
        response = await client.web_search(
            query, count=1, offset=0, safesearch=settings.safesearch, country=settings.country
        )
    except BraveApiError:
        return Redirect(path=f"/search?q={quote(query)}", status_code=303)
    if not response.results:
        return html(render_lucky_not_found(query))
    return Redirect(path=safe_url(response.results[0].url), status_code=303)


async def _run_search(client: BraveClient, params: SearchParams, settings: AppSettings) -> str:
    started = time.monotonic()
    if params.tab is Tab.IMAGES:
        images = await client.image_search(
            params.query,
            count=IMAGE_RESULT_COUNT,
            safesearch=settings.safesearch,
            country=settings.country,
        )
        return render_image_results(params, images, time.monotonic() - started)
    if params.tab is Tab.NEWS:
        news = await client.news_search(
            params.query,
            count=RESULTS_PER_PAGE,
            offset=params.offset,
            safesearch=settings.safesearch,
            country=settings.country,
            freshness=params.freshness,
        )
        return render_news_results(params, news, time.monotonic() - started)
    web = await client.web_search(
        params.query,
        count=RESULTS_PER_PAGE,
        offset=params.offset,
        safesearch=settings.safesearch,
        country=settings.country,
        freshness=params.freshness,
        spellcheck=params.spellcheck,
    )
    return render_web_results(params, web, time.monotonic() - started)
