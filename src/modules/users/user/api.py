from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path

from core.methods import get_connection, require_permissions
from modules.users.schemes import UserRead
from modules.users.user.responses import USER_LOGIN_CONFLICT, USER_NOT_FOUND, USER_ROLE_404
from modules.users.user.schemes import UserCreate, UserCreateResponse, UserUpdate

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
    raise NotImplementedError


@router.get(
    "/{user_id}",
    response_model=UserRead,
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
    raise NotImplementedError


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
    raise NotImplementedError


@router.delete(
    "/{user_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('user.delete'))],
    summary="Удалить пользователя",
    responses={404: USER_NOT_FOUND},
)
async def delete_user(
    connection: Annotated[Connection, Depends(get_connection)],
    user_id: Annotated[int, Path(ge=1, description="Идентификатор пользователя")]
):
    raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError
