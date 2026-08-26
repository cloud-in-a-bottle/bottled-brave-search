from urllib.parse import urlsplit

from server.brave.models import MetaUrl
from server.brave.models import Profile
from server.views import icons
from server.views.html import escape
from server.views.html import safe_url


def site_name(url: str, meta_url: MetaUrl | None, profile: Profile | None) -> str:
    if profile is not None and profile.name:
        return profile.name
    if meta_url is not None and meta_url.hostname:
        return meta_url.hostname.removeprefix("www.")
    return urlsplit(url).hostname or url


def display_url(url: str, meta_url: MetaUrl | None) -> str:
    if meta_url is not None and meta_url.hostname:
        scheme = meta_url.scheme or "https"
        # Brave's path is already a "› wiki › Otter" breadcrumb; Google separates it from the host with a space.
        crumb = f" {meta_url.path.strip()}" if meta_url.path else ""
        return f"{scheme}://{meta_url.hostname}{crumb}"
    return url


def render_favicon(meta_url: MetaUrl | None, profile: Profile | None, *, size_class: str = "") -> str:
    src = None
    if meta_url is not None and meta_url.favicon:
        src = meta_url.favicon
    elif profile is not None and profile.img:
        src = profile.img
    inner = (
        f'<img src="{escape(safe_url(src))}" alt="" loading="lazy" referrerpolicy="no-referrer">'
        if src
        else f'<span class="favicon-fallback">{icons.GLOBE}</span>'
    )
    return f'<span class="favicon {escape(size_class)}">{inner}</span>'


def render_source_row(url: str, meta_url: MetaUrl | None, profile: Profile | None) -> str:
    return (
        '<div class="source-row">'
        f"{render_favicon(meta_url, profile)}"
        '<div class="source-text">'
        f'<span class="source-name">{escape(site_name(url, meta_url, profile))}</span>'
        f'<span class="source-url">{escape(display_url(url, meta_url))}</span>'
        "</div>"
        "</div>"
    )


def render_result_menu(url: str) -> str:
    host = urlsplit(url).hostname or ""
    site_search = f"/search?q=site%3A{escape(host)}" if host else "/"
    return (
        '<details class="result-menu">'
        f'<summary aria-label="About this result">{icons.MORE_VERT}</summary>'
        '<div class="result-menu-card">'
        f'<div class="result-menu-url">{escape(url)}</div>'
        f'<a href="{escape(safe_url(url))}" target="_blank" rel="noopener noreferrer">Open in a new tab</a>'
        f'<a href="{site_search}">Search only this site</a>'
        "</div>"
        "</details>"
    )
