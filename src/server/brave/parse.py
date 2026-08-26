from server.brave.models import DiscussionResult
from server.brave.models import FaqResult
from server.brave.models import ImageResult
from server.brave.models import ImageSearchResponse
from server.brave.models import Infobox
from server.brave.models import InfoboxAttribute
from server.brave.models import InfoboxProfile
from server.brave.models import MetaUrl
from server.brave.models import NewsResult
from server.brave.models import NewsSearchResponse
from server.brave.models import Profile
from server.brave.models import QueryInfo
from server.brave.models import Thumbnail
from server.brave.models import WebResult
from server.brave.models import WebSearchResponse
from server.json_util import JsonObject
from server.json_util import as_object
from server.json_util import get_bool
from server.json_util import get_int
from server.json_util import get_list
from server.json_util import get_object
from server.json_util import get_objects
from server.json_util import get_str
from server.json_util import get_strs


def _parse_meta_url(obj: JsonObject | None) -> MetaUrl | None:
    if obj is None:
        return None
    return MetaUrl(
        hostname=get_str(obj, "hostname") or get_str(obj, "netloc"),
        favicon=get_str(obj, "favicon"),
        path=get_str(obj, "path"),
        scheme=get_str(obj, "scheme"),
    )


def _parse_thumbnail(obj: JsonObject | None) -> Thumbnail | None:
    if obj is None:
        return None
    src = get_str(obj, "src")
    if src is None:
        return None
    return Thumbnail(src=src, original=get_str(obj, "original"))


def _parse_profile(obj: JsonObject | None) -> Profile | None:
    if obj is None:
        return None
    return Profile(
        name=get_str(obj, "name"),
        long_name=get_str(obj, "long_name"),
        url=get_str(obj, "url"),
        img=get_str(obj, "img"),
    )


def _parse_query(obj: JsonObject | None, fallback: str) -> QueryInfo:
    if obj is None:
        return QueryInfo(original=fallback, altered=None, more_results_available=False)
    altered = get_str(obj, "altered")
    original = get_str(obj, "original") or fallback
    return QueryInfo(
        original=original,
        altered=altered if altered != original else None,
        more_results_available=get_bool(obj, "more_results_available"),
    )


def _parse_web_result(obj: JsonObject) -> WebResult | None:
    title = get_str(obj, "title")
    url = get_str(obj, "url")
    if title is None or url is None:
        return None
    return WebResult(
        title=title,
        url=url,
        description_html=get_str(obj, "description") or "",
        meta_url=_parse_meta_url(get_object(obj, "meta_url")),
        profile=_parse_profile(get_object(obj, "profile")),
        thumbnail=_parse_thumbnail(get_object(obj, "thumbnail")),
        age=get_str(obj, "age"),
        page_age=get_str(obj, "page_age"),
        extra_snippets=get_strs(obj, "extra_snippets"),
    )


def _parse_news_result(obj: JsonObject) -> NewsResult | None:
    title = get_str(obj, "title")
    url = get_str(obj, "url")
    if title is None or url is None:
        return None
    return NewsResult(
        title=title,
        url=url,
        description_html=get_str(obj, "description") or "",
        meta_url=_parse_meta_url(get_object(obj, "meta_url")),
        thumbnail=_parse_thumbnail(get_object(obj, "thumbnail")),
        age=get_str(obj, "age"),
        page_age=get_str(obj, "page_age"),
        is_breaking=get_bool(obj, "breaking"),
    )


def _parse_discussion_result(obj: JsonObject) -> DiscussionResult | None:
    # Discussions wrap their interesting fields in a nested "data" object.
    data = get_object(obj, "data") or obj
    title = get_str(obj, "title") or get_str(data, "title")
    url = get_str(obj, "url")
    if title is None or url is None:
        return None
    return DiscussionResult(
        title=title,
        url=url,
        forum_name=get_str(data, "forum_name"),
        num_answers=get_int(data, "num_answers"),
        score=get_str(data, "score"),
        question=get_str(data, "question") or get_str(obj, "description"),
        top_comment=get_str(data, "top_comment"),
        meta_url=_parse_meta_url(get_object(obj, "meta_url")),
    )


def _parse_faq_result(obj: JsonObject) -> FaqResult | None:
    question = get_str(obj, "question")
    answer = get_str(obj, "answer")
    if question is None or answer is None:
        return None
    return FaqResult(
        question=question,
        answer=answer,
        title=get_str(obj, "title"),
        url=get_str(obj, "url"),
        meta_url=_parse_meta_url(get_object(obj, "meta_url")),
    )


def _parse_infobox_attributes(obj: JsonObject) -> tuple[InfoboxAttribute, ...]:
    attributes: list[InfoboxAttribute] = []
    for entry in get_list(obj, "attributes"):
        # Brave sends attributes as ["Label", "Value"] pairs.
        if isinstance(entry, str) or not isinstance(entry, (list, tuple)) or len(entry) < 2:
            continue
        label, value = entry[0], entry[1]
        if isinstance(label, str) and isinstance(value, str) and label and value:
            attributes.append(InfoboxAttribute(label=label, value=value))
    return tuple(attributes)


def _parse_infobox(obj: JsonObject | None) -> Infobox | None:
    if obj is None:
        return None
    first = next(iter(get_objects(obj, "results")), None)
    if first is None:
        return None
    title = get_str(first, "title")
    if title is None:
        return None
    profiles = tuple(
        InfoboxProfile(name=name, url=url, img=get_str(entry, "img"))
        for entry in get_objects(first, "profiles")
        if (name := get_str(entry, "name")) and (url := get_str(entry, "url"))
    )
    return Infobox(
        title=title,
        subtitle=get_str(first, "subtitle") or get_str(first, "category"),
        description=get_str(first, "long_desc") or get_str(first, "description"),
        thumbnail=_parse_thumbnail(get_object(first, "thumbnail")),
        attributes=_parse_infobox_attributes(first),
        profiles=profiles,
        website_url=get_str(first, "website_url") or get_str(first, "url"),
    )


def _parse_image_result(obj: JsonObject) -> ImageResult | None:
    source_url = get_str(obj, "url")
    thumbnail = _parse_thumbnail(get_object(obj, "thumbnail"))
    if source_url is None or thumbnail is None:
        return None
    properties = get_object(obj, "properties")
    return ImageResult(
        title=get_str(obj, "title") or source_url,
        source_url=source_url,
        thumbnail_src=thumbnail.src,
        full_size_url=get_str(properties, "url") if properties else None,
        width=get_int(properties, "width") if properties else None,
        height=get_int(properties, "height") if properties else None,
        meta_url=_parse_meta_url(get_object(obj, "meta_url")),
    )


def _results_of(payload: JsonObject, section: str) -> tuple[JsonObject, ...]:
    nested = get_object(payload, section)
    return get_objects(nested, "results") if nested else ()


def parse_web_search(payload: object, query: str) -> WebSearchResponse:
    obj = as_object(payload)
    if obj is None:
        raise ValueError("Brave web search returned a non-object payload")
    return WebSearchResponse(
        query=_parse_query(get_object(obj, "query"), query),
        results=tuple(r for r in (_parse_web_result(e) for e in _results_of(obj, "web")) if r is not None),
        news=tuple(r for r in (_parse_news_result(e) for e in _results_of(obj, "news")) if r is not None),
        discussions=tuple(
            r for r in (_parse_discussion_result(e) for e in _results_of(obj, "discussions")) if r is not None
        ),
        faq=tuple(r for r in (_parse_faq_result(e) for e in _results_of(obj, "faq")) if r is not None),
        infobox=_parse_infobox(get_object(obj, "infobox")),
    )


def parse_image_search(payload: object, query: str) -> ImageSearchResponse:
    obj = as_object(payload)
    if obj is None:
        raise ValueError("Brave image search returned a non-object payload")
    return ImageSearchResponse(
        query=_parse_query(get_object(obj, "query"), query),
        results=tuple(r for r in (_parse_image_result(e) for e in get_objects(obj, "results")) if r is not None),
    )


def parse_news_search(payload: object, query: str) -> NewsSearchResponse:
    obj = as_object(payload)
    if obj is None:
        raise ValueError("Brave news search returned a non-object payload")
    return NewsSearchResponse(
        query=_parse_query(get_object(obj, "query"), query),
        results=tuple(r for r in (_parse_news_result(e) for e in get_objects(obj, "results")) if r is not None),
    )
