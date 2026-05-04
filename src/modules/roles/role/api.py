from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path

from core.exceptions import APIException
from core.methods import get_connection, require_permissions
from modules.roles.role import repositories
from modules.roles.role.responses import ROLE_NAME_CONFLICT, ROLE_NOT_FOUND, ROLE_PERMISSION_404
from modules.roles.role.schemes import RoleCreate, RoleCreateResponse, RoleUpdate
from modules.roles.schemes import RoleRead

router = APIRouter()


@router.post(
    "/",
    response_model=RoleCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions('role.create'))],
    summary="Создать новую роль",
    responses={
        409: ROLE_NAME_CONFLICT
    }
)
async def create_role(
    connection: Annotated[Connection, Depends(get_connection)],
    payload: Annotated[RoleCreate, Body()]
):
    existing_by_name = await repositories.exist_role_by_name(connection, payload.name)

    if existing_by_name:
        raise APIException(
            status_code=409,
            code="ROLE_NAME_EXISTS",
            message="Роль с таким именем уже существует"
        )

    role_id = await repositories.create_role(connection, payload.name)
    return RoleCreateResponse(id=role_id)


@router.get(
    "/{role_id}",
    response_model=RoleRead,
    dependencies=[Depends(require_permissions('role.read'))],
    summary="Получить информацию о роли",
    responses={
        404: ROLE_NOT_FOUND
    }
)
async def get_role(
    connection: Annotated[Connection, Depends(get_connection)],
    role_id: Annotated[int, Path(ge=1, description="Идентификатор роли")]
):
    role = await repositories.get_role_by_id(connection, role_id)

    if role is None:
        raise APIException(
            status_code=404,
            code="ROLE_NOT_FOUND",
            message="Роль не найдена"
        )

    return RoleRead(**role)


@router.put(
    "/{role_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('role.update'))],
    summary="Обновить информацию о роли",
    responses={
        404: ROLE_NOT_FOUND,
        409: ROLE_NAME_CONFLICT,
    },
)
async def update_role(
    connection: Annotated[Connection, Depends(get_connection)],
    role_id: Annotated[int, Path(ge=1, description="Идентификатор роли")],
    payload: Annotated[RoleUpdate, Body()]
):
    role = await repositories.get_role_by_id(connection, role_id)

    if role is None:
        raise APIException(
            status_code=404,
            code="ROLE_NOT_FOUND",
            message="Роль не найдена"
        )

    if role['name'] != payload.name:
        existing_by_name = await repositories.exist_role_by_name(connection, payload.name)

        if existing_by_name:
            raise APIException(
                status_code=409,
                code="ROLE_NAME_EXISTS",
                message="Роль с таким именем уже существует"
            )

    await repositories.update_role(connection, role_id, payload.name)


@router.delete(
    "/{role_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('role.delete'))],
    summary="Удалить роль",
    responses={
        404: ROLE_NOT_FOUND
    }
)
async def delete_role(
    connection: Annotated[Connection, Depends(get_connection)],
    role_id: Annotated[int, Path(ge=1, description="Идентификатор роли")]
):
    role = await repositories.get_role_by_id(connection, role_id)

    if not role:
        raise APIException(
            status_code=404,
            code="ROLE_NOT_FOUND",
            message="Роль не найдена"
        )

    await repositories.delete_role(connection, role_id)


@router.post(
    "/{role_id}/permissions",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('role.permission.assign'))],
    summary="Назначить разрешение роли",
    responses={
        404: ROLE_PERMISSION_404
    }
)
async def assign_permission_to_role(
    connection: Annotated[Connection, Depends(get_connection)],
    role_id: Annotated[int, Path(ge=1, description="Идентификатор роли")],
    permission_id: Annotated[int, Body(ge=1, description="Идентификатор разрешения", embed=True)]
):
    role = await repositories.get_role_by_id(connection, role_id)

    if role is None:
        raise APIException(
            status_code=404,
            code="ROLE_NOT_FOUND",
            message="Роль не найдена"
        )

    permission_exists = await repositories.exist_permission_by_id(connection, permission_id)

    if not permission_exists:
        raise APIException(
            status_code=404,
            code="PERMISSION_NOT_FOUND",
            message="Разрешение не найдено"
        )

    await repositories.assign_permission_to_role(connection, role_id, permission_id)


@router.delete(
    "/{role_id}/permissions/{permission_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('role.permission.remove'))],
    summary="Удалить разрешение у роли",
    responses={
        404: ROLE_PERMISSION_404
    }
)
async def remove_permission_from_role(
    connection: Annotated[Connection, Depends(get_connection)],
    role_id: Annotated[int, Path(ge=1, description="Идентификатор роли")],
    permission_id: Annotated[int, Path(ge=1, description="Идентификатор разрешения")]
):
    role = await repositories.get_role_by_id(connection, role_id)

    if role is None:
        raise APIException(
            status_code=404,
            code="ROLE_NOT_FOUND",
            message="Роль не найдена"
        )

    permission_exists = await repositories.exist_permission_by_id(connection, permission_id)

    if not permission_exists:
        raise APIException(
            status_code=404,
            code="PERMISSION_NOT_FOUND",
            message="Разрешение не найдено"
        )

    await repositories.remove_permission_from_role(connection, role_id, permission_id)
