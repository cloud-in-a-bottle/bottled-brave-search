import json
import os

import attr
import httpx
from loguru import logger

from server.brave.errors import BraveApiError
from server.brave.errors import BraveErrorKind
from server.brave.models import ImageSearchResponse
from server.brave.models import NewsSearchResponse
from server.brave.models import WebSearchResponse
from server.brave.parse import parse_image_search
from server.brave.parse import parse_news_search
from server.brave.parse import parse_web_search

DEFAULT_API_BASE_URL = "https://api.search.brave.com/res/v1"
# Overridable so tests can point the client at a local stub of the Brave API.
API_BASE_URL_ENV_VAR = "BRAVE_API_BASE_URL"

DASHBOARD_URL = "https://api-dashboard.search.brave.com/app/keys"
REGISTER_URL = "https://api-dashboard.search.brave.com/register"

# Brave's image endpoint only accepts "off" or "strict".
_IMAGE_SAFESEARCH = {"off": "off", "moderate": "strict", "strict": "strict"}


@attr.s(auto_attribs=True, frozen=True)
class BraveClient:
    api_key: str
    base_url: str = attr.Factory(lambda: os.environ.get(API_BASE_URL_ENV_VAR, DEFAULT_API_BASE_URL))
    timeout_seconds: float = 12.0

    async def _get(self, path: str, params: dict[str, str | int]) -> object:
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key,
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(f"{self.base_url}{path}", params=params, headers=headers)
        except httpx.HTTPError as error:
            raise BraveApiError(
                kind=BraveErrorKind.NETWORK,
                message=f"Could not reach the Brave Search API: {error}",
            ) from error

        if response.status_code != httpx.codes.OK:
            raise _error_for_response(path, response)

        try:
            return json.loads(response.content)
        except json.JSONDecodeError as error:
            raise BraveApiError(
                kind=BraveErrorKind.UPSTREAM,
                message="The Brave Search API returned a response that wasn't valid JSON.",
                status_code=response.status_code,
            ) from error

    async def web_search(
        self,
        query: str,
        *,
        count: int,
        offset: int,
        safesearch: str,
        country: str,
        freshness: str = "",
        spellcheck: bool = True,
    ) -> WebSearchResponse:
        params: dict[str, str | int] = {
            "q": query,
            "count": count,
            "offset": offset,
            "safesearch": safesearch,
            "text_decorations": 1,
            "extra_snippets": 1,
            "spellcheck": 1 if spellcheck else 0,
        }
        if freshness:
            params["freshness"] = freshness
        if country != "ALL":
            params["country"] = country
        return parse_web_search(await self._get("/web/search", params), query)

    async def image_search(self, query: str, *, count: int, safesearch: str, country: str) -> ImageSearchResponse:
        params: dict[str, str | int] = {
            "q": query,
            "count": count,
            "safesearch": _IMAGE_SAFESEARCH[safesearch],
        }
        if country != "ALL":
            params["country"] = country
        return parse_image_search(await self._get("/images/search", params), query)

    async def news_search(
        self, query: str, *, count: int, offset: int, safesearch: str, country: str, freshness: str = ""
    ) -> NewsSearchResponse:
        params: dict[str, str | int] = {
            "q": query,
            "count": count,
            "offset": offset,
            "safesearch": safesearch,
            "extra_snippets": 1,
        }
        if freshness:
            params["freshness"] = freshness
        if country != "ALL":
            params["country"] = country
        return parse_news_search(await self._get("/news/search", params), query)

    async def verify_key(self) -> None:
        """Raise BraveApiError if this key can't perform a web search."""
        await self.web_search("brave search", count=1, offset=0, safesearch="moderate", country="ALL")


# Brave reports a bad or out-of-quota subscription as HTTP 422 with a machine-readable code, not as 401/403,
# so the code is checked before the status.
_ERROR_CODE_KINDS = {
    "SUBSCRIPTION_TOKEN_INVALID": BraveErrorKind.INVALID_KEY,
    "SUBSCRIPTION_TOKEN_MISSING": BraveErrorKind.INVALID_KEY,
    "SUBSCRIPTION_EXPIRED": BraveErrorKind.QUOTA_EXCEEDED,
    "PLAN_EXPIRED": BraveErrorKind.QUOTA_EXCEEDED,
    "QUOTA_EXCEEDED": BraveErrorKind.QUOTA_EXCEEDED,
    "RATE_LIMITED": BraveErrorKind.RATE_LIMITED,
}

_KIND_MESSAGES = {
    BraveErrorKind.INVALID_KEY: "Brave rejected the API key. It may have been revoked, or it may not cover this endpoint.",
    BraveErrorKind.QUOTA_EXCEEDED: "This Brave Search subscription is out of quota.",
    BraveErrorKind.RATE_LIMITED: "Brave rate-limited this request. The free plan allows one query per second — try again shortly.",
}


def _error_for_response(path: str, response: httpx.Response) -> BraveApiError:
    status = response.status_code
    code, detail = _error_from_body(response)
    logger.warning("brave {} failed with {} ({}): {}", path, status, code or "-", detail or response.text[:200])

    kind = _ERROR_CODE_KINDS.get(code or "")
    if kind is not None:
        return BraveApiError(kind=kind, message=detail or _KIND_MESSAGES[kind], status_code=status)

    if status in (httpx.codes.UNAUTHORIZED, httpx.codes.FORBIDDEN):
        return BraveApiError(
            kind=BraveErrorKind.INVALID_KEY,
            message="Brave rejected the API key. It may have been revoked, or it may not cover this endpoint.",
            status_code=status,
        )
    if status == httpx.codes.TOO_MANY_REQUESTS:
        return BraveApiError(
            kind=BraveErrorKind.RATE_LIMITED,
            message="Brave rate-limited this request. The free plan allows one query per second — try again shortly.",
            status_code=status,
        )
    if status == httpx.codes.PAYMENT_REQUIRED:
        return BraveApiError(
            kind=BraveErrorKind.QUOTA_EXCEEDED,
            message="This Brave Search subscription is out of quota.",
            status_code=status,
        )
    if status == httpx.codes.UNPROCESSABLE_ENTITY:
        return BraveApiError(
            kind=BraveErrorKind.BAD_REQUEST,
            message=detail or "Brave rejected the search parameters.",
            status_code=status,
        )
    return BraveApiError(
        kind=BraveErrorKind.UPSTREAM,
        message=detail or f"The Brave Search API returned HTTP {status}.",
        status_code=status,
    )


def _error_from_body(response: httpx.Response) -> tuple[str | None, str | None]:
    """Pull Brave's ``error.code`` and ``error.detail`` out of an error body."""
    try:
        payload = json.loads(response.content)
    except json.JSONDecodeError:
        return None, None
    if not isinstance(payload, dict):
        return None, None
    error = payload.get("error")
    if not isinstance(error, dict):
        return None, None
    code = error.get("code")
    detail = error.get("detail")
    return (
        code if isinstance(code, str) and code else None,
        detail if isinstance(detail, str) and detail else None,
    )
