from typing import Any

import orjson
from fastapi.responses import Response
from pydantic_core import to_jsonable_python


class JSONResponse(Response):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        return orjson.dumps(to_jsonable_python(content))
