from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path, Query

from core.exceptions import APIException
from core.methods import get_connection, require_permissions
from modules.users.schemes import UserReadWithPermissions
from modules.users.user import repositories
from modules.users.user.responses import USER_LOGIN_CONFLICT, USER_NOT_FOUND, USER_ROLE_404, USER_SESSION_404
from modules.users.user.schemes import UserChangePassword, UserCreate, UserCreateResponse, UserSessionsResponse, UserUpdate
from modules.users.utils import hash_password

router = APIRouter()


@router.post(
    "/",
    response_model=UserCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions('user.create'))],
    summary="Создать нового пользователя",
    responses={
        409: USER_LOGIN_CONFLICT
    }
)
async def create_user(
    connection: Annotated[Connection, Depends(get_connection)],
    payload: Annotated[UserCreate, Body()]
):
    existing_by_username = await repositories.exist_user_by_username(connection, payload.username)

    if existing_by_username:
        raise APIException(
            status_code=409,
            code="USER_USERNAME_EXISTS",
            message="Пользователь с таким именем уже существует"
        )

    password_hash = hash_password(payload.password)
    user_id = await repositories.create_user(
        connection,
        payload.name,
        payload.username,
        password_hash,
        payload.is_active
    )
    return UserCreateResponse(id=user_id)


@router.get(
    "/{user_id}",
    response_model=UserReadWithPermissions,
    dependencies=[Depends(require_permissions('user.read'))],
    summary="Получить информацию о пользователе",
    responses={
        404: USER_NOT_FOUND
    }
)
async def get_user(
    connection: Annotated[Connection, Depends(get_connection)],
    user_id: Annotated[int, Path(ge=1, description="Идентификатор пользователя")]
):
    user = await repositories.get_user_by_id(connection, user_id)

    if user is None:
        raise APIException(
            status_code=404,
            code="USER_NOT_FOUND",
            message="Пользователь не найден"
        )

    return UserReadWithPermissions.model_validate(user)


@router.put(
    "/{user_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('user.update'))],
    summary="Обновить информацию о пользователе",
    responses={
        404: USER_NOT_FOUND,
        409: USER_LOGIN_CONFLICT,
    }
)
async def update_user(
    connection: Annotated[Connection, Depends(get_connection)],
    user_id: Annotated[int, Path(ge=1, description="Идентификатор пользователя")],
    payload: Annotated[UserUpdate, Body()]
):
    user = await repositories.get_user_by_id(connection, user_id)

    if user is None:
        raise APIException(
            status_code=404,
            code="USER_NOT_FOUND",
            message="Пользователь не найден"
        )

    if user['username'] != payload.username:
        existing_by_username = await repositories.exist_user_by_username(connection, payload.username)

        if existing_by_username:
            raise APIException(
                status_code=409,
                code="USER_USERNAME_EXISTS",
                message="Пользователь с таким именем уже существует"
            )

    password_hash = hash_password(payload.password)
    await repositories.update_user(
        connection,
        user_id,
        payload.name,
        payload.username,
        password_hash,
        payload.is_active
    )


@router.delete(
    "/{user_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('user.delete'))],
    summary="Удалить пользователя",
    responses={
        404: USER_NOT_FOUND
    }
)
async def delete_user(
    connection: Annotated[Connection, Depends(get_connection)],
    user_id: Annotated[int, Path(ge=1, description="Идентификатор пользователя")]
):
    user = await repositories.get_user_by_id(connection, user_id)

    if not user:
        raise APIException(
            status_code=404,
            code="USER_NOT_FOUND",
            message="Пользователь не найден"
        )

    await repositories.delete_user(connection, user_id)


@router.post(
    "/{user_id}/roles",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('user.role.assign'))],
    summary="Назначить роль пользователю",
    responses={
        404: USER_ROLE_404
    }
)
async def assign_role_to_user(
    connection: Annotated[Connection, Depends(get_connection)],
    user_id: Annotated[int, Path(ge=1, description="Идентификатор пользователя")],
    role_id: Annotated[int, Body(ge=1, description="Идентификатор роли", embed=True)]
):
    user = await repositories.get_user_by_id(connection, user_id)

    if user is None:
        raise APIException(
            status_code=404,
            code="USER_NOT_FOUND",
            message="Пользователь не найден"
        )

    role_exists = await repositories.exist_role_by_id(connection, role_id)

    if not role_exists:
        raise APIException(
            status_code=404,
            code="ROLE_NOT_FOUND",
            message="Роль не найдена"
        )

    await repositories.assign_role_to_user(connection, user_id, role_id)


@router.delete(
    "/{user_id}/roles/{role_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('user.role.remove'))],
    summary="Удалить роль у пользователя",
    responses={
        404: USER_ROLE_404
    }
)
async def remove_role_from_user(
    connection: Annotated[Connection, Depends(get_connection)],
    user_id: Annotated[int, Path(ge=1, description="Идентификатор пользователя")],
    role_id: Annotated[int, Path(ge=1, description="Идентификатор роли")]
):
    user = await repositories.get_user_by_id(connection, user_id)

    if user is None:
        raise APIException(
            status_code=404,
            code="USER_NOT_FOUND",
            message="Пользователь не найден"
        )

    role_exists = await repositories.exist_role_by_id(connection, role_id)

    if not role_exists:
        raise APIException(
            status_code=404,
            code="ROLE_NOT_FOUND",
            message="Роль не найдена"
        )

    await repositories.remove_role_from_user(connection, user_id, role_id)


@router.put(
    "/{user_id}/password",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('user.password.change'))],
    summary="Сменить пароль пользователя",
    responses={
        404: USER_NOT_FOUND
    }
)
async def change_user_password(
    connection: Annotated[Connection, Depends(get_connection)],
    user_id: Annotated[int, Path(ge=1, description="Идентификатор пользователя")],
    payload: Annotated[UserChangePassword, Body()]
):
    user = await repositories.get_user_by_id(connection, user_id)

    if user is None:
        raise APIException(
            status_code=404,
            code="USER_NOT_FOUND",
            message="Пользователь не найден"
        )

    password_hash = hash_password(payload.new_password)
    await repositories.change_user_password(connection, user_id, password_hash)


@router.get(
    "/{user_id}/sessions",
    response_model=UserSessionsResponse,
    dependencies=[Depends(require_permissions('user.sessions.read'))],
    summary="Получить сессии пользователя",
    responses={
        404: USER_NOT_FOUND
    }
)
async def get_user_sessions(
    connection: Annotated[Connection, Depends(get_connection)],
    user_id: Annotated[int, Path(ge=1, description="Идентификатор пользователя")],
    sessions_limit: Annotated[int, Query(ge=1, le=100, description="Количество сессий для отображения")] = 10,
):
    user = await repositories.get_user_by_id(connection, user_id)

    if user is None:
        raise APIException(
            status_code=404,
            code="USER_NOT_FOUND",
            message="Пользователь не найден"
        )

    sessions = await repositories.get_user_sessions(connection, user_id, sessions_limit)
    return UserSessionsResponse.model_validate(sessions)


@router.delete(
    "/{user_id}/sessions/{session_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('user.sessions.terminate'))],
    summary="Завершить сессию пользователя",
    responses={
        404: USER_SESSION_404
    }
)
async def terminate_user_session(
    connection: Annotated[Connection, Depends(get_connection)],
    user_id: Annotated[int, Path(ge=1, description="Идентификатор пользователя")],
    session_id: Annotated[str, Path(description="Идентификатор сессии")]
):
    user = await repositories.get_user_by_id(connection, user_id)

    if user is None:
        raise APIException(
            status_code=404,
            code="USER_NOT_FOUND",
            message="Пользователь не найден"
        )

    session_exists = await repositories.exist_user_session(connection, user_id, session_id)

    if not session_exists:
        raise APIException(
            status_code=404,
            code="SESSION_NOT_FOUND",
            message="Сессия не найдена или уже завершена"
        )

    await repositories.deactivate_user_session(connection, user_id, session_id)
