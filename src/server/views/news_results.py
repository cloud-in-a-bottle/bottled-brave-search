from server.brave.models import NewsResult
from server.brave.models import NewsSearchResponse
from server.search_params import SearchParams
from server.views.formatting import format_seconds
from server.views.html import escape
from server.views.html import join
from server.views.html import safe_url
from server.views.html import sanitize_markup
from server.views.pager import render_pager
from server.views.result_common import render_favicon
from server.views.result_common import site_name


def render_news_results(params: SearchParams, response: NewsSearchResponse, elapsed_seconds: float) -> str:
    if not response.results:
        body = f'<div class="no-results"><p>No news results for <b>{escape(params.query)}</b>.</p></div>'
        pager = ""
    else:
        body = f'<div class="news-list">{join(_render_item(result) for result in response.results)}</div>'
        pager = render_pager(params, has_next=response.query.more_results_available)
    return (
        '<div class="serp-columns"><div class="serp-main">'
        f'<div class="result-stats">News from Brave Search ({format_seconds(elapsed_seconds)} seconds)</div>'
        f"{body}{pager}"
        '</div><div class="serp-side"></div></div>'
    )


def _render_item(result: NewsResult) -> str:
    thumbnail = (
        f'<div class="news-thumb"><img src="{escape(safe_url(result.thumbnail.src))}" alt="" loading="lazy"'
        ' referrerpolicy="no-referrer"></div>'
        if result.thumbnail is not None
        else ""
    )
    badge = '<span class="news-breaking">Breaking</span>' if result.is_breaking else ""
    age = f'<span class="news-age">{escape(result.age)}</span>' if result.age else ""
    return (
        f'<a class="news-item" href="{escape(safe_url(result.url))}">'
        '<div class="news-body">'
        '<div class="news-source">'
        f"{render_favicon(result.meta_url, None, size_class='favicon-sm')}"
        f"<span>{escape(site_name(result.url, result.meta_url, None))}</span>"
        "</div>"
        f'<div class="news-title">{badge}{escape(result.title)}</div>'
        f'<div class="news-snippet">{sanitize_markup(result.description_html)}</div>'
        f'<div class="news-meta">{age}</div>'
        "</div>"
        f"{thumbnail}"
        "</a>"
    )
