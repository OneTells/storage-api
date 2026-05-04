import hashlib
from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends

from core.config import settings
from core.exceptions import APIException
from core.methods import get_connection
from core.methods.authentication import Token
from modules.auth.password.repositories import create_session, get_user_id
from modules.auth.password.responses import PASSWORD_LOGIN_INVALID_CREDENTIALS
from modules.auth.password.schemes import AuthPayload
from modules.auth.schemes import TokenResponse

router = APIRouter()


@router.post(
    "/password",
    response_model=TokenResponse,
    status_code=201,
    summary="Авторизация по логину и паролю",
    responses={
        401: PASSWORD_LOGIN_INVALID_CREDENTIALS
    }
)
async def password_login(
    connection: Annotated[Connection, Depends(get_connection)],
    payload: Annotated[AuthPayload, Body()]
):
    password_hash = hashlib.sha256(payload.password.encode()).hexdigest()
    user_id = await get_user_id(connection, payload.username, password_hash)

    if user_id is None:
        raise APIException(
            status_code=401,
            code="INVALID_DATA",
            message="Неверные учётные данные"
        )

    session_id = await create_session(connection, user_id)

    token = Token.generate(session_id, settings.secret_token)
    return TokenResponse(token=token)
