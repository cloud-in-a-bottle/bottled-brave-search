from enum import Enum

import attr


class BraveErrorKind(Enum):
    INVALID_KEY = "invalid_key"
    RATE_LIMITED = "rate_limited"
    QUOTA_EXCEEDED = "quota_exceeded"
    BAD_REQUEST = "bad_request"
    UPSTREAM = "upstream"
    NETWORK = "network"


@attr.s(auto_attribs=True, frozen=True)
class BraveApiError(Exception):
    kind: BraveErrorKind
    message: str
    status_code: int | None = None

    def __str__(self) -> str:
        return self.message

    @property
    def needs_new_key(self) -> bool:
        return self.kind in (BraveErrorKind.INVALID_KEY, BraveErrorKind.QUOTA_EXCEEDED)
