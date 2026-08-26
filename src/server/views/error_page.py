from server.brave.errors import BraveApiError
from server.search_params import SearchParams
from server.views.html import escape
from server.views.layout import render_document
from server.views.layout import render_footer
from server.views.layout import render_search_header


def render_search_error(params: SearchParams, error: BraveApiError) -> str:
    action = (
        '<p><a class="primary-link" href="/settings">Update your API key in Settings</a></p>'
        if error.needs_new_key
        else ""
    )
    body = (
        f"{render_search_header(params)}"
        '<div class="serp-columns"><div class="serp-main">'
        '<div class="search-error">'
        "<h1>That search didn't go through</h1>"
        f"<p>{escape(error.message)}</p>"
        f"{action}"
        "</div>"
        '</div><div class="serp-side"></div></div>'
        f"{render_footer()}"
    )
    return render_document(f"{params.query} - Brave Search", body, body_class="serp-page")
