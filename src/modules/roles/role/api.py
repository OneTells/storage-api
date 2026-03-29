from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path

from core.methods import get_connection, require_permissions
from core.schemes import ErrorResponse
from modules.roles.role.schemes import RoleCreate, RoleCreateResponse, RoleUpdate

ROLE_NOT_FOUND_RESPONSE = {
    "description": "Роль не найдена",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {"detail": "Роль не найдена"}
        }
    }
}

ROLE_ALREADY_EXISTS_RESPONSE = {
    "description": "Роль с таким именем уже существует",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {"detail": "Роль с таким именем уже существует"}
        }
    }
}

ROLE_OR_PERMISSION_NOT_FOUND_RESPONSE = {
    "description": "Роль или разрешение не найдены",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "role_not_found": {
                    "summary": "Роль не найдена",
                    "value": {"detail": "Роль не найдена"}
                },
                "permission_not_found": {
                    "summary": "Разрешение не найдено",
                    "value": {"detail": "Разрешение не найдено"}
                },
            }
        }
    }
}

router = APIRouter()


@router.post(
    "/",
    response_model=RoleCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions('role.create'))],
    summary="Создать новую роль",
    responses={
        201: {"description": "Роль успешно создана"},
        409: ROLE_ALREADY_EXISTS_RESPONSE,
    }
)
async def create_role(
    connection: Annotated[Connection, Depends(get_connection)],
    payload: Annotated[RoleCreate, Body()]
):
    raise NotImplementedError


@router.put(
    "/{role_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('role.update'))],
    summary="Обновить информацию о роли",
    responses={
        204: {"description": "Роль успешно обновлена"},
        404: ROLE_NOT_FOUND_RESPONSE,
        409: ROLE_ALREADY_EXISTS_RESPONSE,
    }
)
async def update_role(
    connection: Annotated[Connection, Depends(get_connection)],
    role_id: Annotated[int, Path(ge=1, description="Идентификатор роли")],
    payload: Annotated[RoleUpdate, Body()]
):
    raise NotImplementedError


@router.delete(
    "/{role_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('role.delete'))],
    summary="Удалить роль",
    responses={
        204: {"description": "Роль успешно удалена"},
        404: ROLE_NOT_FOUND_RESPONSE,
    }
)
async def delete_role(
    connection: Annotated[Connection, Depends(get_connection)],
    role_id: Annotated[int, Path(ge=1, description="Идентификатор роли")]
):
    raise NotImplementedError


@router.post(
    "/{role_id}/permissions",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('role.permission.assign'))],
    summary="Назначить разрешение роли",
    responses={
        204: {"description": "Разрешение успешно назначено"},
        404: ROLE_OR_PERMISSION_NOT_FOUND_RESPONSE,
    }
)
async def assign_permission_to_role(
    connection: Annotated[Connection, Depends(get_connection)],
    role_id: Annotated[int, Path(ge=1, description="Идентификатор роли")],
    permission_id: Annotated[int, Body(ge=1, description="Идентификатор разрешения")]
):
    raise NotImplementedError


@router.delete(
    "/{role_id}/permissions/{permission_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('role.permission.remove'))],
    summary="Удалить разрешение у роли",
    responses={
        204: {"description": "Разрешение успешно удалено"},
        404: ROLE_OR_PERMISSION_NOT_FOUND_RESPONSE,
    }
)
async def remove_permission_from_role(
    connection: Annotated[Connection, Depends(get_connection)],
    role_id: Annotated[int, Path(ge=1, description="Идентификатор роли")],
    permission_id: Annotated[int, Path(ge=1, description="Идентификатор разрешения")]
):
    raise NotImplementedError
