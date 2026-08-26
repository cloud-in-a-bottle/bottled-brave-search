from server.search_params import FRESHNESS_CHOICES
from server.search_params import SearchParams
from server.search_params import Tab
from server.views import icons
from server.views.html import escape
from server.views.html import join
from server.views.html import query_string

WORDMARK_LETTERS = (("B", "blue"), ("r", "red"), ("a", "yellow"), ("v", "blue"), ("e", "green"))

_TAB_ICONS = {Tab.ALL: icons.SEARCH, Tab.IMAGES: icons.IMAGE, Tab.NEWS: icons.NEWS}


def render_document(title: str, body: str, *, body_class: str = "") -> str:
    return (
        "<!doctype html>"
        '<html lang="en">'
        "<head>"
        '<meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<meta name="referrer" content="no-referrer">'
        '<meta name="color-scheme" content="light dark">'
        f"<title>{escape(title)}</title>"
        '<link rel="icon" href="/static/favicon.svg" type="image/svg+xml">'
        '<link rel="stylesheet" href="/static/style.css">'
        "</head>"
        f'<body class="{escape(body_class)}">{body}'
        '<script src="/static/app.js" defer></script>'
        "</body></html>"
    )


def render_wordmark(class_name: str) -> str:
    letters = join(f'<span class="wm-{color}">{letter}</span>' for letter, color in WORDMARK_LETTERS)
    return f'<span class="wordmark {escape(class_name)}" aria-label="Brave Search">{letters}</span>'


def render_search_box(params: SearchParams, *, autofocus: bool, extra_class: str = "", trailing: str = "") -> str:
    hidden = ""
    if params.tab is not Tab.ALL:
        hidden += f'<input type="hidden" name="tab" value="{escape(params.tab.value)}">'
    if params.freshness:
        hidden += f'<input type="hidden" name="freshness" value="{escape(params.freshness)}">'
    return (
        f'<form class="searchbox {escape(extra_class)}" action="/search" method="get" role="search">'
        '<div class="sb-input-wrap">'
        '<span class="sb-lead-icon">' + icons.SEARCH + "</span>"
        '<input class="sb-input" type="text" name="q" title="Search" autocomplete="off" spellcheck="false"'
        f' value="{escape(params.query)}"{" autofocus" if autofocus else ""}>'
        '<button class="sb-clear" type="button" title="Clear" aria-label="Clear">' + icons.CLOSE + "</button>"
        '<span class="sb-divider"></span>'
        '<button class="sb-submit" type="submit" title="Search" aria-label="Search">' + icons.SEARCH + "</button>"
        "</div>"
        f"{hidden}{trailing}"
        "</form>"
    )


def render_search_header(params: SearchParams) -> str:
    return (
        '<header class="serp-header">'
        '<div class="serp-header-main">'
        f'<a class="serp-logo" href="/" title="Home">{render_wordmark("wordmark-small")}</a>'
        f"{render_search_box(params, autofocus=False)}"
        f'<a class="serp-settings" href="/settings" title="Settings" aria-label="Settings">{icons.SETTINGS}</a>'
        "</div>"
        f"{_render_tabs(params)}"
        "</header>"
    )


def _render_tabs(params: SearchParams) -> str:
    items = join(_render_tab(params, tab) for tab in Tab)
    return (
        '<div class="serp-tabs-row">'
        f'<nav class="serp-tabs">{items}</nav>'
        f"{_render_tools(params)}"
        "</div>"
        f"{_render_tools_panel(params)}"
    )


def _render_tab(params: SearchParams, tab: Tab) -> str:
    is_active = tab is params.tab
    href = "/search" + query_string(params.with_tab(tab).as_query_pairs())
    classes = "serp-tab active" if is_active else "serp-tab"
    aria = ' aria-current="page"' if is_active else ""
    return f'<a class="{classes}" href="{escape(href)}"{aria}><span class="tab-icon">{_TAB_ICONS[tab]}</span>{tab.label}</a>'


def _render_tools(params: SearchParams) -> str:
    # Images search has no freshness filter on Brave's side, so the Tools button is hidden there.
    if params.tab is Tab.IMAGES:
        return ""
    label = "Tools" if not params.freshness else escape(params.freshness_label())
    active = " active" if params.freshness else ""
    return f'<button class="serp-tools-toggle{active}" type="button" data-toggle="tools-panel">{label}</button>'


def _render_tools_panel(params: SearchParams) -> str:
    if params.tab is Tab.IMAGES:
        return ""
    options = join(
        f'<a class="tool-option{" active" if value == params.freshness else ""}"'
        f' href="{escape("/search" + query_string(params.with_freshness(value).as_query_pairs()))}">{escape(label)}</a>'
        for value, label in FRESHNESS_CHOICES
    )
    hidden = "" if params.freshness else " hidden"
    return f'<div class="serp-tools-panel" id="tools-panel"{hidden}><div class="tool-group">{options}</div></div>'


def render_footer(*, sticky: bool = False) -> str:
    classes = "site-footer sticky" if sticky else "site-footer"
    return (
        f'<footer class="{classes}">'
        '<div class="footer-row footer-top">Results from the Brave Search API</div>'
        '<div class="footer-row footer-links">'
        '<div class="footer-links-left">'
        '<a href="https://brave.com/search/api/" target="_blank" rel="noopener">About the API</a>'
        '<a href="https://search.brave.com/help/privacy-policy" target="_blank" rel="noopener">Privacy</a>'
        "</div>"
        '<div class="footer-links-right">'
        '<a href="/settings">Settings</a>'
        "</div>"
        "</div>"
        "</footer>"
    )
