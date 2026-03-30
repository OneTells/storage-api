from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path

from core.methods import get_connection, require_permissions
from core.schemes import ErrorCode, ErrorResponse
from modules.objects.object.schemes import ObjectCreate, ObjectCreateResponse, ObjectUpdate
from modules.objects.schemes import ObjectRead

router = APIRouter()


@router.post(
    "/",
    response_model=ObjectCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions('object.create'))],
    summary="Создать новый объект",
    responses={
        201: {"description": "Объект успешно создан"},
    }
)
async def create_object(
    connection: Annotated[Connection, Depends(get_connection)],
    payload: Annotated[ObjectCreate, Body()]
):
    raise NotImplementedError


@router.get(
    "/{object_id}",
    response_model=ObjectRead,
    dependencies=[Depends(require_permissions('object.read'))],
    summary="Получить информацию об объекте",
    responses={
        200: {"description": "Информация об объекте успешно получена"},
        404: {
            "description": "Объект не найден",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "code": ErrorCode.OBJECT_NOT_FOUND,
                        "message": "Объект не найден",
                        "params": {}
                    }
                }
            }
        },
    }
)
async def get_object(
    connection: Annotated[Connection, Depends(get_connection)],
    object_id: Annotated[int, Path(ge=1, description="Идентификатор объекта")]
):
    raise NotImplementedError


@router.put(
    "/{object_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('object.update'))],
    summary="Обновить информацию об объекте",
    responses={
        204: {"description": "Объект успешно обновлён"},
        404: {
            "description": "Объект не найден",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "code": ErrorCode.OBJECT_NOT_FOUND,
                        "message": "Объект не найден",
                        "params": {}
                    }
                }
            }
        },
    }
)
async def update_object(
    connection: Annotated[Connection, Depends(get_connection)],
    object_id: Annotated[int, Path(ge=1, description="Идентификатор объекта")],
    payload: Annotated[ObjectUpdate, Body()]
):
    raise NotImplementedError


@router.delete(
    "/{object_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('object.delete'))],
    summary="Удалить объект",
    responses={
        204: {"description": "Объект успешно удалён"},
        404: {
            "description": "Объект не найден",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "code": ErrorCode.OBJECT_NOT_FOUND,
                        "message": "Объект не найден",
                        "params": {}
                    }
                }
            }
        },
        409: {
            "description": "Объект не может быть удален, так как есть связанные записи",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "code": ErrorCode.OBJECT_HAS_RELATIONS,
                        "message": "Объект не может быть удален, так как есть связанные записи",
                        "params": {}
                    }
                }
            }
        },
    }
)
async def delete_object(
    connection: Annotated[Connection, Depends(get_connection)],
    object_id: Annotated[int, Path(ge=1, description="Идентификатор объекта")]
):
    raise NotImplementedError
