from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends

from core.methods import get_connection
from modules.auth.password.responses import PASSWORD_LOGIN_INVALID_CREDENTIALS
from modules.auth.password.schemes import AuthPayload
from modules.auth.schemes import TokenResponse

router = APIRouter()


@router.post(
    "/password/login",
    response_model=TokenResponse,
    status_code=201,
    summary="Авторизация по логину и паролю",
    responses={
        201: {"description": "Авторизация успешна"},
        401: PASSWORD_LOGIN_INVALID_CREDENTIALS,
    },
)
async def password_login(
    connection: Annotated[Connection, Depends(get_connection)],
    payload: Annotated[AuthPayload, Body()]
):
    raise NotImplementedError
