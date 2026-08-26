from litestar import MediaType
from litestar import Request
from litestar import Response
from litestar.datastructures import State


def html(body: str, *, status_code: int = 200, no_store: bool = False) -> Response[str]:
    headers = {"Cache-Control": "no-store"} if no_store else None
    return Response(content=body, media_type=MediaType.HTML, status_code=status_code, headers=headers)


async def form_value(request: Request[None, None, State], key: str) -> str:
    form = await request.form()
    value = form.get(key)
    return value.strip() if isinstance(value, str) else ""
