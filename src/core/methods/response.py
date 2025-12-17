from typing import Any

from fastapi.responses import Response
from orjson import dumps
from pydantic_core import to_jsonable_python


class JSONResponse(Response):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        return dumps(to_jsonable_python(content))
