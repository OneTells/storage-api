from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, Query
from orjson import loads

from core.exceptions import APIException
from core.methods import get_connection, get_current_user, require_permissions
from core.schemes import UserModel
from modules.users.profile import repositories
from modules.users.profile.schemes import ProfileChangePassword, ProfileRead, ProfileUpdate
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

    data = dict(profile_data)
    data['sessions'] = [loads(x) for x in data['sessions']]
    data['roles'] = [loads(x) for x in data['roles']]
    data['permissions'] = [loads(x) for x in data['permissions']]

    return ProfileRead.model_validate(data)


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
    payload: Annotated[ProfileUpdate, Body()],
):
    current_username = await repositories.get_user_username(connection, user.id)

    if current_username is None:
        raise APIException(
            status_code=404,
            code="USER_NOT_FOUND",
            message="Пользователь не найден"
        )

    if current_username != payload.username:
        existing_by_username = await repositories.exist_user_by_username(connection, payload.username)

        if existing_by_username:
            raise APIException(
                status_code=409,
                code="USER_USERNAME_EXISTS",
                message="Пользователь с таким именем уже существует"
            )

    await repositories.update_user(
        connection,
        user.id,
        payload.name,
        payload.username
    )


@router.put(
    "/profile/password",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('profile.update'))],
    summary="Сменить пароль текущего пользователя",
)
async def change_password(
    connection: Annotated[Connection, Depends(get_connection)],
    user: Annotated[UserModel, Depends(get_current_user)],
    payload: Annotated[ProfileChangePassword, Body()],
):
    password_hash = hash_password(payload.new_password)
    await repositories.update_user_password(
        connection,
        user.id,
        password_hash
    )
