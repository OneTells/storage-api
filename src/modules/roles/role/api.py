from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path

from core.methods import get_connection, require_permissions
from core.schemes import ErrorCode, ErrorResponse
from modules.roles.role.schemes import RoleCreate, RoleCreateResponse, RoleUpdate

router = APIRouter()


@router.post(
    "/",
    response_model=RoleCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions('role.create'))],
    summary="Создать новую роль",
    responses={
        201: {"description": "Роль успешно создана"},
        409: {
            "description": "Роль с таким именем уже существует",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "code": ErrorCode.ROLE_ALREADY_EXISTS,
                        "message": "Роль с таким именем уже существует",
                        "params": {}
                    }
                }
            }
        },
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
        404: {
            "description": "Роль не найдена",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "code": ErrorCode.ROLE_NOT_FOUND,
                        "message": "Роль не найдена",
                        "params": {}
                    }
                }
            }
        },
        409: {
            "description": "Роль с таким именем уже существует",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "code": ErrorCode.ROLE_ALREADY_EXISTS,
                        "message": "Роль с таким именем уже существует",
                        "params": {}
                    }
                }
            }
        },
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
        404: {
            "description": "Роль не найдена",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "code": ErrorCode.ROLE_NOT_FOUND,
                        "message": "Роль не найдена",
                        "params": {}
                    }
                }
            }
        },
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
        404: {
            "description": "Роль или разрешение не найдены",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "role_not_found": {
                            "summary": "Роль не найдена",
                            "value": {
                                "code": ErrorCode.ROLE_NOT_FOUND,
                                "message": "Роль не найдена",
                                "params": {}
                            }
                        },
                        "permission_not_found": {
                            "summary": "Разрешение не найдено",
                            "value": {
                                "code": ErrorCode.PERMISSION_NOT_FOUND,
                                "message": "Разрешение не найдено",
                                "params": {}
                            }
                        },
                    }
                }
            }
        },
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
        404: {
            "description": "Роль или разрешение не найдены",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "role_not_found": {
                            "summary": "Роль не найдена",
                            "value": {
                                "code": ErrorCode.ROLE_NOT_FOUND,
                                "message": "Роль не найдена",
                                "params": {}
                            }
                        },
                        "permission_not_found": {
                            "summary": "Разрешение не найдено",
                            "value": {
                                "code": ErrorCode.PERMISSION_NOT_FOUND,
                                "message": "Разрешение не найдено",
                                "params": {}
                            }
                        },
                    }
                }
            }
        },
    }
)
async def remove_permission_from_role(
    connection: Annotated[Connection, Depends(get_connection)],
    role_id: Annotated[int, Path(ge=1, description="Идентификатор роли")],
    permission_id: Annotated[int, Path(ge=1, description="Идентификатор разрешения")]
):
    raise NotImplementedError
