from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path, Query

from core.methods import get_connection, require_permissions
from modules.categories.schemes import CategoriesReadResponse
from modules.objects.object.responses import OBJECT_DELETE_CONFLICT, OBJECT_NOT_FOUND
from modules.objects.object.schemes import ObjectCreate, ObjectCreateResponse, ObjectUpdate
from modules.objects.schemes import ObjectRead

router = APIRouter()


@router.post(
    "/",
    response_model=ObjectCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions('object.create'))],
    summary="Создать новый объект",
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
        404: OBJECT_NOT_FOUND
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
        404: OBJECT_NOT_FOUND
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
        404: OBJECT_NOT_FOUND,
        409: OBJECT_DELETE_CONFLICT,
    }
)
async def delete_object(
    connection: Annotated[Connection, Depends(get_connection)],
    object_id: Annotated[int, Path(ge=1, description="Идентификатор объекта")]
):
    raise NotImplementedError


@router.get(
    "/{object_id}/categories",
    response_model=CategoriesReadResponse,
    dependencies=[Depends(require_permissions("object.read"))],
    summary="Получить категории объекта",
    responses={
        404: OBJECT_NOT_FOUND
    }
)
async def get_object_categories(
    connection: Annotated[Connection, Depends(get_connection)],
    object_id: Annotated[int, Path(ge=1, description="Идентификатор объекта")],
    page: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    limit: Annotated[int, Query(ge=1, le=1000, description="Количество элементов на странице")] = 100,
):
    raise NotImplementedError
