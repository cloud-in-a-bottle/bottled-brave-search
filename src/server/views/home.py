from server.search_params import SearchParams
from server.search_params import Tab
from server.views.html import escape
from server.views.html import query_string
from server.views.layout import render_document
from server.views.layout import render_footer
from server.views.layout import render_search_box
from server.views.layout import render_wordmark

_EMPTY = SearchParams(query="", tab=Tab.ALL, start=0, freshness="")

_BUTTONS = (
    '<div class="home-buttons">'
    '<button class="home-button" type="submit">Brave Search</button>'
    '<button class="home-button" type="submit" formaction="/lucky">I\'m Feeling Lucky</button>'
    "</div>"
)


def render_home_page() -> str:
    body = (
        '<div class="home-topbar"><a href="/settings">Settings</a></div>'
        '<main class="home-main">'
        f'<div class="home-logo">{render_wordmark("wordmark-large")}</div>'
        f"{render_search_box(_EMPTY, autofocus=True, extra_class='searchbox-home', trailing=_BUTTONS)}"
        "</main>"
        f"{render_footer(sticky=True)}"
    )
    return render_document("Brave Search", body, body_class="home-page")


def render_lucky_not_found(query: str) -> str:
    href = escape("/search" + query_string((("q", query),)))
    body = (
        '<main class="home-main">'
        f'<div class="home-logo">{render_wordmark("wordmark-large")}</div>'
        f'<p class="home-message">No result to jump to for <b>{escape(query)}</b>.</p>'
        f'<p class="home-message"><a href="{href}">Search instead</a></p>'
        "</main>"
    )
    return render_document("Brave Search", body, body_class="home-page")
