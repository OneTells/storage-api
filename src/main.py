import orjson
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import RedirectResponse, Response
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from core.config import settings
from core.methods import Lifespan
from core.middleware import LoggerMiddleware
from core.schemes import INTERNAL_ERROR_RESPONSE
from modules.api import main_router

app = FastAPI(
    title="Storage API",
    version="1.0.0",
    lifespan=Lifespan.run,
    responses={
        500: INTERNAL_ERROR_RESPONSE,
    }
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
        orjson.dumps({"detail": "Внутренняя ошибка сервера"}),
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        media_type="application/json"
    )
