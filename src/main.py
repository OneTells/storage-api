from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse as DefaultJSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_422_UNPROCESSABLE_CONTENT

from core.methods import Lifespan
from core.methods.response import JSONResponse
from core.middleware import LoggerMiddleware
from modules.api import main_router

app = FastAPI(
    title="Storage API",
    version="1.0.0",
    lifespan=Lifespan.run,
    default_response_class=JSONResponse
)

app.add_middleware(LoggerMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['https://ya.ru'],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(main_router)


@app.get("/")
def get_default():
    return RedirectResponse("https://ya.ru")


@app.exception_handler(Exception)
def exception_handler(_: Request, __: Exception) -> DefaultJSONResponse:
    return DefaultJSONResponse(
        {"detail": "Внутренняя ошибка сервера"},
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(_: Request, __: RequestValidationError) -> DefaultJSONResponse:
    return DefaultJSONResponse(
        {"detail": "Необрабатываемая сущность"},
        status_code=HTTP_422_UNPROCESSABLE_CONTENT,
    )
