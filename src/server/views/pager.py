from server.search_params import MAX_PAGES
from server.search_params import SearchParams
from server.views import icons
from server.views.html import escape
from server.views.html import join
from server.views.html import query_string

# The pager spells the wordmark with one repeated letter per page, the way Google's "Gooooooogle" pager does.
_PREFIX = (("B", "blue"), ("r", "red"))
_REPEATED = ("a", "yellow")
_SUFFIX = (("v", "blue"), ("e", "green"))
_REPEAT_COLORS = ("yellow", "blue", "green", "red")


def render_pager(params: SearchParams, *, has_next: bool) -> str:
    last_page = MAX_PAGES if has_next else params.page
    pages = tuple(range(1, last_page + 1))
    if len(pages) < 2:
        return ""

    cells = [_render_nav_cell(params, params.page - 1, "Previous", icons.CHEVRON_LEFT)] if params.page > 1 else []
    cells += [_render_letter_cell(letter, color) for letter, color in _PREFIX]
    cells += [_render_page_cell(params, page, index) for index, page in enumerate(pages)]
    cells += [_render_letter_cell(letter, color) for letter, color in _SUFFIX]
    if has_next and params.page < MAX_PAGES:
        cells.append(_render_nav_cell(params, params.page + 1, "Next", icons.CHEVRON_RIGHT))

    return f'<nav class="pager" aria-label="Page navigation"><div class="pager-row">{join(cells)}</div></nav>'


def _page_href(params: SearchParams, page: int) -> str:
    return escape("/search" + query_string(params.with_page(page).as_query_pairs()))


def _render_letter_cell(letter: str, color: str) -> str:
    return f'<span class="pager-cell pager-static"><span class="pager-letter wm-{color}">{letter}</span></span>'


def _render_page_cell(params: SearchParams, page: int, index: int) -> str:
    letter, _ = _REPEATED
    color = _REPEAT_COLORS[index % len(_REPEAT_COLORS)]
    if page == params.page:
        return (
            '<span class="pager-cell pager-current" aria-current="page">'
            f'<span class="pager-letter wm-current">{letter}</span>'
            f'<span class="pager-number">{page}</span>'
            "</span>"
        )
    return (
        f'<a class="pager-cell" href="{_page_href(params, page)}" aria-label="Page {page}">'
        f'<span class="pager-letter wm-{color}">{letter}</span>'
        f'<span class="pager-number">{page}</span>'
        "</a>"
    )


def _render_nav_cell(params: SearchParams, page: int, label: str, icon: str) -> str:
    direction = label.lower()
    return (
        f'<a class="pager-cell pager-nav pager-{direction}" href="{_page_href(params, page)}">'
        f'<span class="pager-chevron">{icon}</span>'
        f'<span class="pager-number">{label}</span>'
        "</a>"
    )
