from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, Query

from core.exceptions import APIException
from core.methods import get_connection, get_current_user, require_permissions
from core.schemes import UserModel
from modules.users.profile import repositories
from modules.users.profile.schemes import ProfileRead
from modules.users.user.schemes import UserUpdate
from modules.users.utils import hash_password

router = APIRouter()


@router.get(
    "/profile",
    response_model=ProfileRead,
    dependencies=[Depends(require_permissions('profile.read'))],
    summary="Получить профиль текущего пользователя",
)
async def get_profile(
    connection: Annotated[Connection, Depends(get_connection)],
    user: Annotated[UserModel, Depends(get_current_user)],
    sessions_limit: Annotated[int, Query(ge=1, le=100, description="Количество сессий для отображения")] = 10,
):
    profile_data = await repositories.get_user_profile_data(connection, user.id, sessions_limit)

    if profile_data is None:
        raise APIException(
            status_code=404,
            code="USER_NOT_FOUND",
            message="Пользователь не найден"
        )

    return ProfileRead.model_validate(profile_data)


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
    current_username = await repositories.get_user_username(connection, user.id)

    if current_username is None:
        raise APIException(
            status_code=404,
            code="USER_NOT_FOUND",
            message="Пользователь не найден"
        )

    if current_username != payload.username:
        existing_by_username = await repositories.exist_user_by_username(
            connection,
            payload.username,
            exclude_user_id=user.id
        )

        if existing_by_username:
            raise APIException(
                status_code=409,
                code="USER_USERNAME_EXISTS",
                message="Пользователь с таким именем уже существует"
            )

    password_hash = hash_password(payload.password)
    await repositories.update_user(
        connection,
        user.id,
        payload.name,
        payload.username,
        password_hash,
        payload.is_active
    )
