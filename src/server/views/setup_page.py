from server.brave.client import DASHBOARD_URL
from server.brave.client import REGISTER_URL
from server.views import icons
from server.views.html import escape
from server.views.layout import render_document
from server.views.layout import render_wordmark

_STEPS = (
    (
        "Create a Brave Search API account",
        f'Sign up at <a href="{REGISTER_URL}" target="_blank" rel="noopener">api-dashboard.search.brave.com</a>. '
        "Brave asks for a card even on the free plan — it is used to verify identity, not charged.",
    ),
    (
        "Pick a plan",
        'Choose the <b>Free</b> plan under "Data for Search" for up to 2,000 queries a month at one query per '
        "second, or a paid plan if you want more headroom. Image and news results need a plan that covers those "
        "endpoints.",
    ),
    (
        "Generate an API key",
        f'Open <a href="{DASHBOARD_URL}" target="_blank" rel="noopener">API Keys</a> in the dashboard, create a key, '
        "and copy it. It looks like <code>BSA...</code>.",
    ),
)


def render_setup_page(*, error: str | None = None) -> str:
    steps = "".join(
        f'<li><div class="step-title">{title}</div><div class="step-body">{body}</div></li>' for title, body in _STEPS
    )
    banner = f'<div class="form-error">{escape(error)}</div>' if error else ""
    body = (
        '<main class="setup-main">'
        '<div class="setup-card">'
        f'<div class="setup-logo">{render_wordmark("wordmark-medium")}</div>'
        "<h1>Connect your Brave Search API key</h1>"
        '<p class="setup-lead">This app searches the web through Brave\'s Search API. It needs your own API key, '
        "which is stored in this app's private database on your OpenHost instance and never leaves it.</p>"
        f'<ol class="setup-steps">{steps}</ol>'
        f"{banner}"
        '<form class="key-form" method="post" action="/setup">'
        '<label for="api_key">Brave Search API key</label>'
        f'<div class="key-input-wrap">{icons.KEY}'
        '<input id="api_key" name="api_key" type="password" autocomplete="off" spellcheck="false" required'
        ' placeholder="BSA...">'
        '<button class="key-reveal" type="button" data-reveal="api_key">Show</button>'
        "</div>"
        '<button class="primary-button" type="submit">Save and verify</button>'
        '<p class="key-hint">The key is checked against Brave with a single test query before it is saved.</p>'
        "</form>"
        "</div>"
        "</main>"
    )
    return render_document("Set up Brave Search", body, body_class="setup-page")
