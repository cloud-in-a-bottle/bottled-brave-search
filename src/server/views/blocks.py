from urllib.parse import urlsplit

from server.brave.models import DiscussionResult
from server.brave.models import FaqResult
from server.brave.models import Infobox
from server.brave.models import NewsResult
from server.views import icons
from server.views.html import escape
from server.views.html import join
from server.views.html import safe_url
from server.views.html import sanitize_markup
from server.views.html import strip_markup
from server.views.result_common import render_favicon
from server.views.result_common import site_name

TOP_STORIES_LIMIT = 3
FAQ_LIMIT = 4
DISCUSSIONS_LIMIT = 4


def render_top_stories(results: tuple[NewsResult, ...]) -> str:
    if not results:
        return ""
    cards = join(_render_top_story(result) for result in results[:TOP_STORIES_LIMIT])
    return (
        '<section class="block top-stories">'
        '<h2 class="block-heading">Top stories</h2>'
        f'<div class="top-stories-grid">{cards}</div>'
        "</section>"
    )


def _render_top_story(result: NewsResult) -> str:
    thumbnail = (
        f'<div class="story-thumb"><img src="{escape(safe_url(result.thumbnail.src))}" alt="" loading="lazy"'
        ' referrerpolicy="no-referrer"></div>'
        if result.thumbnail is not None
        else ""
    )
    age = f'<div class="story-age">{escape(result.age)}</div>' if result.age else ""
    return (
        f'<a class="story-card" href="{escape(safe_url(result.url))}">'
        f"{thumbnail}"
        '<div class="story-source">'
        f"{render_favicon(result.meta_url, None, size_class='favicon-sm')}"
        f"<span>{escape(site_name(result.url, result.meta_url, None))}</span>"
        "</div>"
        f'<div class="story-title">{escape(result.title)}</div>'
        f"{age}"
        "</a>"
    )


def render_people_also_ask(results: tuple[FaqResult, ...]) -> str:
    if not results:
        return ""
    rows = join(_render_faq_row(result) for result in results[:FAQ_LIMIT])
    return (
        '<section class="block paa">'
        '<h2 class="block-heading">People also ask</h2>'
        f'<div class="paa-list">{rows}</div>'
        "</section>"
    )


def _render_faq_row(result: FaqResult) -> str:
    source = ""
    if result.url is not None:
        source = (
            '<div class="paa-source">'
            f"{render_favicon(result.meta_url, None, size_class='favicon-sm')}"
            f'<a href="{escape(safe_url(result.url))}">{escape(site_name(result.url, result.meta_url, None))}</a>'
            "</div>"
        )
    return (
        '<details class="paa-item">'
        f'<summary><span>{escape(result.question)}</span><span class="paa-chevron">{icons.CHEVRON_DOWN}</span></summary>'
        f'<div class="paa-answer">{sanitize_markup(result.answer)}{source}</div>'
        "</details>"
    )


def render_discussions(results: tuple[DiscussionResult, ...]) -> str:
    if not results:
        return ""
    items = join(_render_discussion(result) for result in results[:DISCUSSIONS_LIMIT])
    return (
        '<section class="block discussions">'
        '<h2 class="block-heading">Discussions and forums</h2>'
        f'<div class="discussion-list">{items}</div>'
        "</section>"
    )


def _render_discussion(result: DiscussionResult) -> str:
    forum = result.forum_name or site_name(result.url, result.meta_url, None)
    meta_bits = []
    if result.num_answers is not None:
        meta_bits.append(f"{result.num_answers} answer{'s' if result.num_answers != 1 else ''}")
    if result.score:
        meta_bits.append(result.score)
    meta = f'<div class="discussion-meta">{escape(" · ".join(meta_bits))}</div>' if meta_bits else ""
    snippet_text = result.top_comment or result.question
    snippet = f'<div class="discussion-snippet">{escape(strip_markup(snippet_text))}</div>' if snippet_text else ""
    return (
        f'<a class="discussion-item" href="{escape(safe_url(result.url))}">'
        '<div class="discussion-source">'
        f"{render_favicon(result.meta_url, None, size_class='favicon-sm')}"
        f"<span>{escape(forum)}</span>"
        "</div>"
        f'<div class="discussion-title">{escape(result.title)}</div>'
        f"{snippet}{meta}"
        "</a>"
    )


def render_knowledge_panel(infobox: Infobox) -> str:
    image = (
        f'<div class="kp-image"><img src="{escape(safe_url(infobox.thumbnail.src))}" alt="" loading="lazy"'
        ' referrerpolicy="no-referrer"></div>'
        if infobox.thumbnail is not None
        else ""
    )
    subtitle = f'<div class="kp-subtitle">{escape(infobox.subtitle)}</div>' if infobox.subtitle else ""
    description = (
        f'<div class="kp-description">{sanitize_markup(infobox.description)}</div>' if infobox.description else ""
    )
    website = (
        f'<a class="kp-website" href="{escape(safe_url(infobox.website_url))}">'
        f"{icons.GLOBE}<span>{escape(_hostname_label(infobox.website_url))}</span></a>"
        if infobox.website_url
        else ""
    )
    attributes = (
        '<dl class="kp-attributes">'
        + join(
            f"<dt>{escape(attribute.label)}</dt><dd>{escape(attribute.value)}</dd>" for attribute in infobox.attributes
        )
        + "</dl>"
        if infobox.attributes
        else ""
    )
    profiles = (
        '<div class="kp-profiles">'
        + join(
            f'<a href="{escape(safe_url(profile.url))}" title="{escape(profile.name)}">'
            + (
                f'<img src="{escape(safe_url(profile.img))}" alt="" loading="lazy" referrerpolicy="no-referrer">'
                if profile.img
                else ""
            )
            + f"<span>{escape(profile.name)}</span></a>"
            for profile in infobox.profiles
        )
        + "</div>"
        if infobox.profiles
        else ""
    )
    return (
        '<aside class="knowledge-panel">'
        f"{image}"
        f'<h2 class="kp-title">{escape(infobox.title)}</h2>'
        f"{subtitle}{description}{website}{attributes}{profiles}"
        "</aside>"
    )


def _hostname_label(url: str) -> str:
    return (urlsplit(url).hostname or url).removeprefix("www.")
