from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Depends

from core.methods import get_connection, get_current_user
from core.schemes import FORBIDDEN_RESPONSE, UNAUTHORIZED_RESPONSE, UserModel
from modules.auth.password.api import router as password_router

router = APIRouter(prefix="/auth", tags=["Авторизация"])
router.include_router(password_router)


@router.post(
    "/logout",
    response_model=None,
    status_code=204,
    summary="Завершить сессию (логаут)",
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: FORBIDDEN_RESPONSE,
    }
)
async def logout(
    connection: Annotated[Connection, Depends(get_connection)],
    user: Annotated[UserModel, Depends(get_current_user)]
):
    raise NotImplementedError
