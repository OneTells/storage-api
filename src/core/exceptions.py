from typing import Any

from .schemes.responses import ErrorCode


class APIException(Exception):

    def __init__(
        self,
        *,
        code: ErrorCode,
        message: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None
    ) -> None:
        self.headers = headers

        self.code = code
        self.message = message
        self.params = params or {}
