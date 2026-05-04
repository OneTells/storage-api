from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path

from core.exceptions import APIException
from core.methods import get_connection, require_permissions
from modules.permissions.permission import repositories
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
        409: PERMISSION_409
    }
)
async def create_permission(
    connection: Annotated[Connection, Depends(get_connection)],
    payload: Annotated[PermissionCreate, Body()]
):
    existing_by_name = await repositories.exist_permission_by_name(connection, payload.name)

    if existing_by_name:
        raise APIException(
            status_code=409,
            code="PERMISSION_NAME_EXISTS",
            message="Разрешение с таким именем уже существует"
        )

    existing_by_codename = await repositories.exist_permission_by_codename(connection, payload.codename)

    if existing_by_codename:
        raise APIException(
            status_code=409,
            code="PERMISSION_CODENAME_EXISTS",
            message="Разрешение с таким кодовым именем уже существует"
        )

    permission_id = await repositories.create_permission(connection, payload.name, payload.codename)
    return PermissionCreateResponse(id=permission_id)


@router.get(
    "/{permission_id}",
    response_model=PermissionRead,
    dependencies=[Depends(require_permissions('permission.read'))],
    summary="Получить информацию о разрешении",
    responses={
        404: PERMISSION_NOT_FOUND
    }
)
async def get_permission(
    connection: Annotated[Connection, Depends(get_connection)],
    permission_id: Annotated[int, Path(ge=1, description="Идентификатор разрешения")]
):
    permission = await repositories.get_permission_by_id(connection, permission_id)

    if permission is None:
        raise APIException(
            status_code=404,
            code="PERMISSION_NOT_FOUND",
            message="Разрешение не найдено"
        )

    return PermissionRead(**permission)


@router.put(
    "/{permission_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('permission.update'))],
    summary="Обновить информацию о разрешении",
    responses={
        404: PERMISSION_NOT_FOUND,
        409: PERMISSION_409,
    }
)
async def update_permission(
    connection: Annotated[Connection, Depends(get_connection)],
    permission_id: Annotated[int, Path(ge=1, description="Идентификатор разрешения")],
    payload: Annotated[PermissionUpdate, Body()]
):
    permission = await repositories.get_permission_by_id(connection, permission_id)

    if permission is None:
        raise APIException(
            status_code=404,
            code="PERMISSION_NOT_FOUND",
            message="Разрешение не найдено"
        )

    if permission['name'] != payload.name:
        existing_by_name = await repositories.exist_permission_by_name(connection, payload.name)

        if existing_by_name:
            raise APIException(
                status_code=409,
                code="PERMISSION_NAME_EXISTS",
                message="Разрешение с таким именем уже существует"
            )

    if permission['codename'] != payload.codename:
        existing_by_codename = await repositories.exist_permission_by_codename(connection, payload.codename)

        if existing_by_codename:
            raise APIException(
                status_code=409,
                code="PERMISSION_CODENAME_EXISTS",
                message="Разрешение с таким кодовым именем уже существует"
            )

    await repositories.update_permission(connection, permission_id, payload.name, payload.codename)


@router.delete(
    "/{permission_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('permission.delete'))],
    summary="Удалить разрешение",
    responses={
        404: PERMISSION_NOT_FOUND
    }
)
async def delete_permission(
    connection: Annotated[Connection, Depends(get_connection)],
    permission_id: Annotated[int, Path(ge=1, description="Идентификатор разрешения")]
):
    permission = await repositories.get_permission_by_id(connection, permission_id)

    if not permission:
        raise APIException(
            status_code=404,
            code="PERMISSION_NOT_FOUND",
            message="Разрешение не найдено"
        )

    await repositories.delete_permission(connection, permission_id)
