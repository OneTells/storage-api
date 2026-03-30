from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path

from core.methods import get_connection, require_permissions
from modules.permissions.permission.responses import PERMISSION_409, PERMISSION_NOT_FOUND
from modules.permissions.permission.schemes import PermissionCreate, PermissionCreateResponse, PermissionUpdate
from modules.permissions.schemes import PermissionRead

router = APIRouter()


@router.post(
    "/",
    response_model=PermissionCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions('permission.create'))],
    summary="Создать новое разрешение",
    responses={
        201: {"description": "Разрешение успешно создано"},
        409: PERMISSION_409,
    }
)
async def create_permission(
    connection: Annotated[Connection, Depends(get_connection)],
    payload: Annotated[PermissionCreate, Body()]
):
    raise NotImplementedError


@router.get(
    "/{permission_id}",
    response_model=PermissionRead,
    dependencies=[Depends(require_permissions('permission.read'))],
    summary="Получить информацию о разрешении",
    responses={
        200: {"description": "Информация о разрешении успешно получена"},
        404: PERMISSION_NOT_FOUND,
    }
)
async def get_permission(
    connection: Annotated[Connection, Depends(get_connection)],
    permission_id: Annotated[int, Path(ge=1, description="Идентификатор разрешения")]
):
    raise NotImplementedError


@router.put(
    "/{permission_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('permission.update'))],
    summary="Обновить информацию о разрешении",
    responses={
        204: {"description": "Разрешение успешно обновлено"},
        404: PERMISSION_NOT_FOUND,
        409: PERMISSION_409,
    }
)
async def update_permission(
    connection: Annotated[Connection, Depends(get_connection)],
    permission_id: Annotated[int, Path(ge=1, description="Идентификатор разрешения")],
    payload: Annotated[PermissionUpdate, Body()]
):
    raise NotImplementedError


@router.delete(
    "/{permission_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('permission.delete'))],
    summary="Удалить разрешение",
    responses={
        204: {"description": "Разрешение успешно удалено"},
        404: PERMISSION_NOT_FOUND,
    }
)
async def delete_permission(
    connection: Annotated[Connection, Depends(get_connection)],
    permission_id: Annotated[int, Path(ge=1, description="Идентификатор разрешения")]
):
    raise NotImplementedError
