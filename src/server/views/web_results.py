from server.brave.models import WebResult
from server.brave.models import WebSearchResponse
from server.search_params import SearchParams
from server.views.blocks import render_discussions
from server.views.blocks import render_knowledge_panel
from server.views.blocks import render_people_also_ask
from server.views.blocks import render_top_stories
from server.views.formatting import format_result_date
from server.views.formatting import format_seconds
from server.views.html import escape
from server.views.html import join
from server.views.html import query_string
from server.views.html import safe_url
from server.views.html import sanitize_markup
from server.views.pager import render_pager
from server.views.result_common import render_result_menu
from server.views.result_common import render_source_row


def render_web_results(params: SearchParams, response: WebSearchResponse, elapsed_seconds: float) -> str:
    if not response.results:
        return _render_no_results(params, elapsed_seconds)

    column = (
        _render_spelling_notice(params, response)
        + _render_stats(elapsed_seconds)
        + _render_interleaved(response)
        + render_pager(params, has_next=response.query.more_results_available)
    )
    panel = render_knowledge_panel(response.infobox) if response.infobox is not None else ""
    return f'<div class="serp-columns"><div class="serp-main">{column}</div><div class="serp-side">{panel}</div></div>'


def _render_interleaved(response: WebSearchResponse) -> str:
    """Slot the feature blocks between web results the way Google mixes them into the result column."""
    results = response.results
    sections = [
        _render_results(results[:3]),
        render_top_stories(response.news),
        _render_results(results[3:6]),
        render_people_also_ask(response.faq),
        _render_results(results[6:9]),
        render_discussions(response.discussions),
        _render_results(results[9:]),
    ]
    return f'<div class="results">{join(sections)}</div>'


def _render_results(results: tuple[WebResult, ...]) -> str:
    return join(_render_result(result) for result in results)


def _render_result(result: WebResult) -> str:
    date = format_result_date(result.page_age, result.age)
    prefix = f'<span class="snippet-date">{escape(date)}</span><span class="snippet-dash"> — </span>' if date else ""
    snippet = (
        f'<div class="result-snippet">{prefix}{sanitize_markup(result.description_html)}</div>'
        if result.description_html
        else ""
    )
    thumbnail = (
        f'<div class="result-thumb"><img src="{escape(safe_url(result.thumbnail.src))}" alt="" loading="lazy"'
        ' referrerpolicy="no-referrer"></div>'
        if result.thumbnail is not None
        else ""
    )
    return (
        '<div class="result">'
        '<div class="result-body">'
        '<div class="result-head">'
        f'<a class="result-link" href="{escape(safe_url(result.url))}">'
        f"{render_source_row(result.url, result.meta_url, result.profile)}"
        f"<h3>{escape(result.title)}</h3>"
        "</a>"
        f"{render_result_menu(result.url)}"
        "</div>"
        f"{snippet}"
        "</div>"
        f"{thumbnail}"
        "</div>"
    )


def _render_stats(elapsed_seconds: float) -> str:
    return f'<div class="result-stats">Results from Brave Search ({format_seconds(elapsed_seconds)} seconds)</div>'


def _render_spelling_notice(params: SearchParams, response: WebSearchResponse) -> str:
    altered = response.query.altered
    if altered is None:
        return ""
    original_href = escape("/search" + query_string(params.with_spellcheck(False).as_query_pairs()))
    return (
        '<div class="spelling-notice">'
        f'<div class="spelling-primary">Showing results for <b><i>{escape(altered)}</i></b></div>'
        f'<div class="spelling-secondary">Search instead for <a href="{original_href}"><i>{escape(params.query)}</i></a></div>'
        "</div>"
    )


def _render_no_results(params: SearchParams, elapsed_seconds: float) -> str:
    return (
        '<div class="serp-columns"><div class="serp-main">'
        f"{_render_stats(elapsed_seconds)}"
        '<div class="no-results">'
        f"<p>Your search - <b>{escape(params.query)}</b> - did not match any documents.</p>"
        "<p>Suggestions:</p>"
        "<ul>"
        "<li>Make sure all words are spelled correctly.</li>"
        "<li>Try different keywords.</li>"
        "<li>Try more general keywords.</li>"
        "<li>Try fewer keywords.</li>"
        "</ul>"
        "</div>"
        '</div><div class="serp-side"></div></div>'
    )
