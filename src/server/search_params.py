from enum import Enum

import attr

RESULTS_PER_PAGE = 10
IMAGE_RESULT_COUNT = 60
# Brave caps `offset` at 9, so page N is offset N-1.
MAX_PAGES = 10


class Tab(Enum):
    ALL = "all"
    IMAGES = "images"
    NEWS = "news"

    @property
    def label(self) -> str:
        return {Tab.ALL: "All", Tab.IMAGES: "Images", Tab.NEWS: "News"}[self]


FRESHNESS_CHOICES: tuple[tuple[str, str], ...] = (
    ("", "Any time"),
    ("pd", "Past 24 hours"),
    ("pw", "Past week"),
    ("pm", "Past month"),
    ("py", "Past year"),
)
_FRESHNESS_VALUES = frozenset(value for value, _ in FRESHNESS_CHOICES)


@attr.s(auto_attribs=True, frozen=True)
class SearchParams:
    query: str
    tab: Tab
    start: int
    freshness: str
    spellcheck: bool = True

    @property
    def page(self) -> int:
        return self.start // RESULTS_PER_PAGE + 1

    @property
    def offset(self) -> int:
        return self.start // RESULTS_PER_PAGE

    def with_page(self, page: int) -> "SearchParams":
        return attr.evolve(self, start=(page - 1) * RESULTS_PER_PAGE)

    def with_tab(self, tab: Tab) -> "SearchParams":
        return attr.evolve(self, tab=tab, start=0)

    def with_spellcheck(self, spellcheck: bool) -> "SearchParams":
        return attr.evolve(self, spellcheck=spellcheck, start=0)

    def with_freshness(self, freshness: str) -> "SearchParams":
        return attr.evolve(self, freshness=freshness, start=0)

    def freshness_label(self) -> str:
        return next(label for value, label in FRESHNESS_CHOICES if value == self.freshness)

    def as_query_pairs(self) -> tuple[tuple[str, str], ...]:
        pairs: list[tuple[str, str]] = [("q", self.query)]
        if self.tab is not Tab.ALL:
            pairs.append(("tab", self.tab.value))
        if self.freshness:
            pairs.append(("freshness", self.freshness))
        if self.start:
            pairs.append(("start", str(self.start)))
        if not self.spellcheck:
            pairs.append(("spellcheck", "0"))
        return tuple(pairs)


def parse_search_params(query: str, tab: str, start: str, freshness: str, spellcheck: str) -> SearchParams:
    return SearchParams(
        query=query.strip(),
        tab=_parse_tab(tab),
        start=_parse_start(start),
        freshness=freshness if freshness in _FRESHNESS_VALUES else "",
        spellcheck=spellcheck != "0",
    )


def _parse_tab(value: str) -> Tab:
    try:
        return Tab(value)
    except ValueError:
        return Tab.ALL


def _parse_start(value: str) -> int:
    try:
        start = int(value)
    except ValueError:
        return 0
    clamped = max(0, min(start, (MAX_PAGES - 1) * RESULTS_PER_PAGE))
    return clamped - clamped % RESULTS_PER_PAGE
