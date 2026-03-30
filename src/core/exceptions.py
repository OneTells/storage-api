from typing import Any

from .schemes.openapi_responses import ErrorCode


class APIException(Exception):

    def __init__(
        self,
        status_code: int,
        code: ErrorCode,
        message: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status_code = status_code
        self.headers = headers

        self.code = code
        self.message = message
        self.params = params or {}
