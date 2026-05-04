from typing import Any


class APIException(Exception):

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None
    ) -> None:
        self.status_code: int = status_code
        self.code: str = code
        self.message: str = message
        self.details: dict[str, Any] = details or {}
        self.headers: dict[str, str] = headers or {}

    def __str__(self) -> str:
        return f"{self.status_code} {self.code}: {self.message}"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"status_code={self.status_code!r}, "
            f"code={self.code!r}, "
            f"message={self.message!r}, "
            f"details={self.details!r}, "
            f"headers={self.headers!r}"
            f")"
        )
