from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends

from core.methods import get_connection, get_current_user, require_permissions
from core.schemes import UserModel
from modules.users.schemes import UserRead
from modules.users.user.schemes import UserUpdate

router = APIRouter()


@router.get(
    "/profile",
    response_model=UserRead,
    dependencies=[Depends(require_permissions('profile.read'))],
    summary="Получить профиль текущего пользователя",
)
async def get_profile(
    connection: Annotated[Connection, Depends(get_connection)],
    user: Annotated[UserModel, Depends(get_current_user)],
):
    raise NotImplementedError


@router.put(
    "/profile",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('profile.update'))],
    summary="Сменить данные профиля текущего пользователя",
)
async def update_profile(
    connection: Annotated[Connection, Depends(get_connection)],
    user: Annotated[UserModel, Depends(get_current_user)],
    payload: Annotated[UserUpdate, Body()],
):
    raise NotImplementedError
