import time

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Scope


def get_real_ip(scope: Scope) -> str:
    for key, value in scope["headers"]:
        if key == b"x-real-ip":
            return value.decode("latin-1")

    return scope["client"][0]


class LoggerMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter_ns()

        try:
            response = await call_next(request)
        except Exception as error:
            logger.exception(
                f"Ошибка в api: {error}. IP={get_real_ip(request.scope)}. "
                f"Request({request.method}; {request.url}; headers={request.headers}). "
                f"Время исполнения: {int((time.perf_counter_ns() - start_time) / 1_000_000)} мс"
            )

            raise error

        logger.debug(
            f"Запрос к api. IP={get_real_ip(request.scope)}. "
            f"Request({request.method}; {request.url}; headers={request.headers}). "
            f"Response({response.status_code}). "
            f"Время исполнения: {int((time.perf_counter_ns() - start_time) / 1_000_000)} мс"
        )

        return response
