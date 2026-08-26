import attr


@attr.s(auto_attribs=True, frozen=True)
class MetaUrl:
    hostname: str | None
    favicon: str | None
    path: str | None
    scheme: str | None


@attr.s(auto_attribs=True, frozen=True)
class Thumbnail:
    src: str
    original: str | None


@attr.s(auto_attribs=True, frozen=True)
class Profile:
    name: str | None
    long_name: str | None
    url: str | None
    img: str | None


@attr.s(auto_attribs=True, frozen=True)
class WebResult:
    title: str
    url: str
    # Brave marks matched query terms with <strong>; kept as markup and sanitized at render time.
    description_html: str
    meta_url: MetaUrl | None
    profile: Profile | None
    thumbnail: Thumbnail | None
    age: str | None
    page_age: str | None
    extra_snippets: tuple[str, ...]


@attr.s(auto_attribs=True, frozen=True)
class NewsResult:
    title: str
    url: str
    description_html: str
    meta_url: MetaUrl | None
    thumbnail: Thumbnail | None
    age: str | None
    page_age: str | None
    is_breaking: bool


@attr.s(auto_attribs=True, frozen=True)
class DiscussionResult:
    title: str
    url: str
    forum_name: str | None
    num_answers: int | None
    score: str | None
    question: str | None
    top_comment: str | None
    meta_url: MetaUrl | None


@attr.s(auto_attribs=True, frozen=True)
class FaqResult:
    question: str
    answer: str
    title: str | None
    url: str | None
    meta_url: MetaUrl | None


@attr.s(auto_attribs=True, frozen=True)
class InfoboxAttribute:
    label: str
    value: str


@attr.s(auto_attribs=True, frozen=True)
class InfoboxProfile:
    name: str
    url: str
    img: str | None


@attr.s(auto_attribs=True, frozen=True)
class Infobox:
    title: str
    subtitle: str | None
    description: str | None
    thumbnail: Thumbnail | None
    attributes: tuple[InfoboxAttribute, ...]
    profiles: tuple[InfoboxProfile, ...]
    website_url: str | None


@attr.s(auto_attribs=True, frozen=True)
class QueryInfo:
    original: str
    altered: str | None
    more_results_available: bool


@attr.s(auto_attribs=True, frozen=True)
class WebSearchResponse:
    query: QueryInfo
    results: tuple[WebResult, ...]
    news: tuple[NewsResult, ...]
    discussions: tuple[DiscussionResult, ...]
    faq: tuple[FaqResult, ...]
    infobox: Infobox | None


@attr.s(auto_attribs=True, frozen=True)
class ImageResult:
    title: str
    # The page the image was found on.
    source_url: str
    thumbnail_src: str
    full_size_url: str | None
    width: int | None
    height: int | None
    meta_url: MetaUrl | None

    @property
    def aspect_ratio(self) -> float:
        if self.width and self.height:
            return self.width / self.height
        return 4 / 3


@attr.s(auto_attribs=True, frozen=True)
class ImageSearchResponse:
    query: QueryInfo
    results: tuple[ImageResult, ...]


@attr.s(auto_attribs=True, frozen=True)
class NewsSearchResponse:
    query: QueryInfo
    results: tuple[NewsResult, ...]
