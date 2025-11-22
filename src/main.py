from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import ORJSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_422_UNPROCESSABLE_CONTENT

from core.config import settings
from core.methods import Lifespan
from core.middleware import LoggerMiddleware
from modules.api import main_router

app = FastAPI(
    title="Storage API",
    version="1.0.0",
    lifespan=Lifespan.run,
    default_response_class=ORJSONResponse
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
def exception_handler(_: Request, __: Exception) -> ORJSONResponse:
    return ORJSONResponse(
        {"detail": "Внутренняя ошибка сервера"},
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(_: Request, __: RequestValidationError) -> ORJSONResponse:
    return ORJSONResponse(
        {"detail": "Необрабатываемая сущность"},
        status_code=HTTP_422_UNPROCESSABLE_CONTENT,
    )
