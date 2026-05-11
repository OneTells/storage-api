from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import RedirectResponse, Response
from orjson import dumps
from starlette.status import HTTP_422_UNPROCESSABLE_CONTENT, HTTP_500_INTERNAL_SERVER_ERROR

from core.config import settings
from core.exceptions import APIException
from core.methods import lifespan
from core.middlewares import LoggerMiddleware
from core.schemes import INTERNAL_ERROR_RESPONSE, UNPROCESSABLE_ENTITY_RESPONSE
from modules.api import main_router

app = FastAPI(
    title="Everium API",
    version="1.0.0",
    lifespan=lifespan,
    responses={
        422: UNPROCESSABLE_ENTITY_RESPONSE,
        500: INTERNAL_ERROR_RESPONSE,
    }
)

app.add_middleware(
    CORSMiddleware,  # type: ignore
    **settings.cors_config.model_dump()
)
app.add_middleware(LoggerMiddleware)

app.include_router(main_router)


@app.get("/", include_in_schema=False)
def redirect_to_base_url() -> RedirectResponse:
    return RedirectResponse(settings.base_url)


@app.exception_handler(APIException)
async def api_exception_handler(_: Request, exc: APIException) -> Response:
    return Response(
        status_code=exc.status_code,
        content=dumps(
            {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        ),
        headers=exc.headers,
        media_type="application/json"
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(_: Request, exc: RequestValidationError) -> Response:
    return Response(
        status_code=HTTP_422_UNPROCESSABLE_CONTENT,
        content=dumps(
            {
                "code": "UNPROCESSABLE_ENTITY",
                "message": "Необрабатываемая сущность",
                "details": {
                    'errors': exc.errors()
                }
            }
        ),
        media_type="application/json"
    )


@app.exception_handler(Exception)
def exception_handler(_: Request, __: Exception) -> Response:
    return Response(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content=dumps(
            {
                "code": "INTERNAL_ERROR",
                "message": "Внутренняя ошибка сервера",
                "details": {}
            }
        ),
        media_type="application/json"
    )
