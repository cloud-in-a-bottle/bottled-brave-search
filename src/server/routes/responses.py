from litestar import MediaType
from litestar import Request
from litestar import Response
from litestar.datastructures import State


def html(body: str, *, status_code: int = 200) -> Response[str]:
    return Response(content=body, media_type=MediaType.HTML, status_code=status_code)


async def form_value(request: Request[None, None, State], key: str) -> str:
    form = await request.form()
    value = form.get(key)
    return value.strip() if isinstance(value, str) else ""
