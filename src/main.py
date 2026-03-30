import orjson
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import RedirectResponse, Response
from pydantic_core import to_jsonable_python
from starlette.status import HTTP_422_UNPROCESSABLE_CONTENT, HTTP_500_INTERNAL_SERVER_ERROR

from core.config import settings
from core.exceptions import APIException
from core.methods import Lifespan
from core.middleware import LoggerMiddleware
from core.schemes import ErrorCode, INTERNAL_ERROR_RESPONSE, UNPROCESSABLE_ENTITY_RESPONSE
from core.schemes.responses import ERROR_CODE_HTTP_STATUS
from modules.api import main_router

app = FastAPI(
    title="Storage API",
    version="1.0.0",
    lifespan=Lifespan.run,
    responses={
        422: UNPROCESSABLE_ENTITY_RESPONSE,
        500: INTERNAL_ERROR_RESPONSE,
    },
)

app.add_middleware(LoggerMiddleware)
app.add_middleware(
    CORSMiddleware,
    **settings.cors_config.model_dump()
)

app.include_router(main_router)


@app.get("/", include_in_schema=False)
def redirect_to_base_url() -> RedirectResponse:
    return RedirectResponse(settings.base_url)


@app.exception_handler(Exception)
def exception_handler(_: Request, __: Exception) -> Response:
    return Response(
        orjson.dumps(
            {
                "code": ErrorCode.INTERNAL_ERROR,
                "message": "Внутренняя ошибка сервера",
                "params": {}
            }
        ),
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        media_type="application/json"
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(_: Request, exc: RequestValidationError) -> Response:
    return Response(
        orjson.dumps(
            {
                "code": ErrorCode.UNPROCESSABLE_ENTITY,
                "message": "Необрабатываемая сущность",
                "params": {"errors": to_jsonable_python(exc.errors())},
            }
        ),
        status_code=HTTP_422_UNPROCESSABLE_CONTENT,
        media_type="application/json",
    )


@app.exception_handler(APIException)
def validation_api_exception_handler(_: Request, exception: APIException) -> Response:
    return Response(
        orjson.dumps(
            {
                "code": exception.code,
                "message": exception.message,
                "params": exception.params
            }
        ),
        status_code=ERROR_CODE_HTTP_STATUS[exception.code],
        headers=exception.headers,
        media_type="application/json"
    )
