from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path

from core.methods import get_connection, require_permissions
from core.schemes import ErrorCode, ErrorResponse
from modules.users.schemes import UserRead
from modules.users.user.schemes import UserCreate, UserCreateResponse, UserUpdate

router = APIRouter()


@router.post(
    "/",
    response_model=UserCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions('user.create'))],
    summary="Создать нового пользователя",
    responses={
        201: {"description": "Пользователь успешно создан"},
        409: {
            "description": "Пользователь с таким логином уже существует",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "code": ErrorCode.USER_LOGIN_ALREADY_EXISTS,
                        "message": "Пользователь с таким логином уже существует",
                        "params": {}
                    }
                }
            }
        },
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
        200: {"description": "Информация о пользователе успешно получена"},
        404: {
            "description": "Пользователь не найден",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "code": ErrorCode.USER_NOT_FOUND,
                        "message": "Пользователь не найден",
                        "params": {}
                    }
                }
            }
        },
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
        204: {"description": "Пользователь успешно обновлён"},
        404: {
            "description": "Пользователь не найден",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "code": ErrorCode.USER_NOT_FOUND,
                        "message": "Пользователь не найден",
                        "params": {}
                    }
                }
            }
        },
        409: {
            "description": "Пользователь с таким логином уже существует",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "code": ErrorCode.USER_LOGIN_ALREADY_EXISTS,
                        "message": "Пользователь с таким логином уже существует",
                        "params": {}
                    }
                }
            }
        },
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
    responses={
        204: {"description": "Пользователь успешно удалён"},
        404: {
            "description": "Пользователь не найден",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "code": ErrorCode.USER_NOT_FOUND,
                        "message": "Пользователь не найден",
                        "params": {}
                    }
                }
            }
        },
    }
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
        204: {"description": "Роль успешно назначена"},
        404: {
            "description": "Пользователь не найден",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "user_not_found": {
                            "summary": "Пользователь не найден",
                            "value": {
                                "code": ErrorCode.USER_NOT_FOUND,
                                "message": "Пользователь не найден",
                                "params": {}
                            }
                        },
                        "role_not_found": {
                            "summary": "Роль не найдена",
                            "value": {
                                "code": ErrorCode.ROLE_NOT_FOUND,
                                "message": "Роль не найдена",
                                "params": {}
                            }
                        },
                    }
                }
            }
        }
    }
)
async def assign_role_to_user(
    connection: Annotated[Connection, Depends(get_connection)],
    user_id: Annotated[int, Path(ge=1, description="Идентификатор пользователя")],
    role_id: Annotated[int, Body(ge=1, description="Идентификатор роли")]
):
    raise NotImplementedError


@router.delete(
    "/{user_id}/roles/{role_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('user.role.remove'))],
    summary="Удалить роль у пользователя",
    responses={
        204: {"description": "Роль успешно удалена"},
        404: {
            "description": "Пользователь не найден",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "user_not_found": {
                            "summary": "Пользователь не найден",
                            "value": {
                                "code": ErrorCode.USER_NOT_FOUND,
                                "message": "Пользователь не найден",
                                "params": {}
                            }
                        },
                        "role_not_found": {
                            "summary": "Роль не найдена",
                            "value": {
                                "code": ErrorCode.ROLE_NOT_FOUND,
                                "message": "Роль не найдена",
                                "params": {}
                            }
                        },
                    }
                }
            }
        }
    }
)
async def remove_role_from_user(
    connection: Annotated[Connection, Depends(get_connection)],
    user_id: Annotated[int, Path(ge=1, description="Идентификатор пользователя")],
    role_id: Annotated[int, Path(ge=1, description="Идентификатор роли")]
):
    raise NotImplementedError
