from server.brave.models import ImageResult
from server.brave.models import ImageSearchResponse
from server.search_params import SearchParams
from server.views.formatting import format_seconds
from server.views.html import escape
from server.views.html import join
from server.views.html import safe_url
from server.views.result_common import render_favicon
from server.views.result_common import site_name

# Rows are justified the way Google Images does it: every tile is scaled to a common height, and flex-grow
# proportional to the tile's aspect ratio stretches the last row's leftovers to fill the width.
_ROW_HEIGHT_PX = 180


def render_image_results(params: SearchParams, response: ImageSearchResponse, elapsed_seconds: float) -> str:
    if not response.results:
        return _render_empty(params, elapsed_seconds)
    tiles = join(_render_tile(result) for result in response.results)
    return (
        '<div class="serp-columns"><div class="serp-main serp-main-wide">'
        f'<div class="result-stats">Images from Brave Search ({format_seconds(elapsed_seconds)} seconds)</div>'
        f'<div class="image-grid">{tiles}</div>'
        '<div class="image-grid-end">End of results</div>'
        "</div></div>"
    )


def _render_tile(result: ImageResult) -> str:
    ratio = max(0.4, min(result.aspect_ratio, 3.0))
    width = round(_ROW_HEIGHT_PX * ratio)
    return (
        f'<a class="image-tile" href="{escape(safe_url(result.source_url))}"'
        f' style="flex-grow:{width};flex-basis:{width}px" title="{escape(result.title)}">'
        '<span class="image-tile-sizer">'
        f'<img src="{escape(safe_url(result.thumbnail_src))}" alt="{escape(result.title)}" loading="lazy"'
        ' referrerpolicy="no-referrer">'
        "</span>"
        f'<span class="image-tile-title">{escape(result.title)}</span>'
        '<span class="image-tile-source">'
        f"{render_favicon(result.meta_url, None, size_class='favicon-sm')}"
        f"<span>{escape(site_name(result.source_url, result.meta_url, None))}</span>"
        "</span>"
        "</a>"
    )


def _render_empty(params: SearchParams, elapsed_seconds: float) -> str:
    return (
        '<div class="serp-columns"><div class="serp-main serp-main-wide">'
        f'<div class="result-stats">Images from Brave Search ({format_seconds(elapsed_seconds)} seconds)</div>'
        f'<div class="no-results"><p>No images found for <b>{escape(params.query)}</b>.</p></div>'
        "</div></div>"
    )
