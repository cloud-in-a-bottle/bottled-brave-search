from server.brave.client import DASHBOARD_URL
from server.countries import COUNTRIES
from server.settings_store import SAFESEARCH_CHOICES
from server.settings_store import AppSettings
from server.views import icons
from server.views.html import escape
from server.views.html import join
from server.views.layout import render_document
from server.views.layout import render_wordmark

_SAFESEARCH_LABELS = {"off": "Off", "moderate": "Moderate", "strict": "Strict"}


def render_settings_page(settings: AppSettings, *, error: str | None = None, notice: str | None = None) -> str:
    banner = f'<div class="form-error">{escape(error)}</div>' if error else ""
    if notice:
        banner += f'<div class="form-notice">{escape(notice)}</div>'
    body = (
        '<main class="settings-main">'
        '<div class="settings-card">'
        f'<div class="settings-header"><a href="/">{render_wordmark("wordmark-medium")}</a><h1>Settings</h1></div>'
        f"{banner}"
        f"{_render_key_section(settings)}"
        f"{_render_preferences_section(settings)}"
        '<div class="settings-footer"><a href="/">Back to search</a></div>'
        "</div>"
        "</main>"
    )
    return render_document("Settings", body, body_class="settings-page")


def _render_key_section(settings: AppSettings) -> str:
    current = (
        f'<div class="current-key">{icons.KEY}<span>Current key: <code>{escape(_mask(settings.brave_api_key))}</code></span></div>'
        if settings.brave_api_key is not None
        else '<div class="current-key">No API key is configured.</div>'
    )
    remove = (
        '<form method="post" action="/settings/key/remove" class="inline-form">'
        '<button class="danger-button" type="submit">Remove key</button>'
        "</form>"
        if settings.brave_api_key is not None
        else ""
    )
    return (
        '<section class="settings-section">'
        "<h2>Brave Search API key</h2>"
        f"{current}"
        '<form class="key-form" method="post" action="/settings/key">'
        f'<div class="key-input-wrap">{icons.KEY}'
        '<input id="api_key" name="api_key" type="password" autocomplete="off" spellcheck="false" required'
        ' placeholder="Paste a new key to replace it">'
        '<button class="key-reveal" type="button" data-reveal="api_key">Show</button>'
        "</div>"
        '<div class="button-row">'
        '<button class="primary-button" type="submit">Save and verify</button>'
        f"{remove}"
        "</div>"
        "</form>"
        f'<p class="key-hint">Manage your keys at <a href="{DASHBOARD_URL}" target="_blank" rel="noopener">the Brave '
        "API dashboard</a>.</p>"
        "</section>"
    )


def _render_preferences_section(settings: AppSettings) -> str:
    safesearch = join(
        f'<label class="radio"><input type="radio" name="safesearch" value="{escape(choice)}"'
        f"{' checked' if choice == settings.safesearch else ''}><span>{_SAFESEARCH_LABELS[choice]}</span></label>"
        for choice in SAFESEARCH_CHOICES
    )
    options = join(
        f'<option value="{escape(code)}"{" selected" if code == settings.country else ""}>{escape(name)}</option>'
        for code, name in COUNTRIES
    )
    return (
        '<section class="settings-section">'
        "<h2>Search preferences</h2>"
        '<form method="post" action="/settings/preferences">'
        '<div class="field"><div class="field-label">SafeSearch</div>'
        f'<div class="radio-row">{safesearch}</div></div>'
        '<div class="field"><label class="field-label" for="country">Region</label>'
        f'<select id="country" name="country">{options}</select></div>'
        '<button class="primary-button" type="submit">Save preferences</button>'
        "</form>"
        "</section>"
    )


def _mask(key: str) -> str:
    if len(key) <= 8:
        return "•" * len(key)
    return f"{key[:4]}{'•' * 12}{key[-4:]}"
