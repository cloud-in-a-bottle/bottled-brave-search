import attr
from litestar import get


@attr.s(auto_attribs=True, frozen=True)
class HealthStatus:
    status: str


@get("/health", sync_to_thread=False, include_in_schema=False)
def health() -> HealthStatus:
    return HealthStatus(status="ok")
