from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path, Query

from core.methods import get_connection, require_permissions
from modules.categories.category.responses import (
    CATEGORY_DELETE_CONFLICT,
    CATEGORY_NOT_FOUND,
    CATEGORY_OBJECT_404,
    CATEGORY_SUBCATEGORY_404,
)
from modules.categories.schemes import (
    CategoryCreate,
    CategoryCreateResponse,
    CategoryRead,
    CategoryUpdate,
    SubcategoriesReadResponse,
)
from modules.objects.schemes import ObjectsReadResponse

router = APIRouter()


@router.post(
    "/",
    response_model=CategoryCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions("category.create"))],
    summary="Создать новую категорию",
)
async def create_category(
    connection: Annotated[Connection, Depends(get_connection)],
    payload: Annotated[CategoryCreate, Body()],
):
    raise NotImplementedError


@router.get(
    "/{category_id}",
    response_model=CategoryRead,
    dependencies=[Depends(require_permissions("category.read"))],
    summary="Получить информацию о категории",
    responses={
        404: CATEGORY_NOT_FOUND
    }
)
async def get_category(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1, description="Идентификатор категории")],
):
    raise NotImplementedError


@router.put(
    "/{category_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("category.update"))],
    summary="Обновить информацию о категории",
    responses={
        404: CATEGORY_NOT_FOUND
    }
)
async def update_category(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1, description="Идентификатор категории")],
    payload: Annotated[CategoryUpdate, Body()],
):
    raise NotImplementedError


@router.delete(
    "/{category_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("category.delete"))],
    summary="Удалить категорию",
    responses={
        404: CATEGORY_NOT_FOUND,
        409: CATEGORY_DELETE_CONFLICT
    }
)
async def delete_category(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1, description="Идентификатор категории")],
):
    raise NotImplementedError


@router.get(
    "/{category_id}/subcategories",
    response_model=SubcategoriesReadResponse,
    dependencies=[Depends(require_permissions("category.read"))],
    summary="Получить подкатегории категории",
    responses={
        404: CATEGORY_NOT_FOUND
    }
)
async def get_subcategories(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1, description="Идентификатор категории")],
    page: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    limit: Annotated[int, Query(ge=1, le=1000, description="Количество элементов на странице")] = 100,
):
    raise NotImplementedError


@router.get(
    "/{category_id}/objects",
    response_model=ObjectsReadResponse,
    dependencies=[Depends(require_permissions("category.read"))],
    summary="Получить объекты категории",
    responses={
        404: CATEGORY_NOT_FOUND
    }
)
async def get_category_objects(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1, description="Идентификатор категории")],
    page: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    limit: Annotated[int, Query(ge=1, le=1000, description="Количество элементов на странице")] = 100,
    is_active: Annotated[bool | None, Query(description="Фильтр по активности объекта")] = None,
):
    raise NotImplementedError


@router.post(
    "/{category_id}/objects",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("category.object.assign"))],
    summary="Привязать объект к категории",
    responses={
        404: CATEGORY_OBJECT_404
    }
)
async def bind_object_to_category(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1, description="Идентификатор категории")],
    object_id: Annotated[int, Body(ge=1, description="Идентификатор объекта")],
):
    raise NotImplementedError


@router.delete(
    "/{category_id}/objects/{object_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("category.object.remove"))],
    summary="Отвязать объект от категории",
    responses={
        404: CATEGORY_OBJECT_404
    }
)
async def unbind_object_from_category(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1, description="Идентификатор категории")],
    object_id: Annotated[int, Path(ge=1, description="Идентификатор объекта")],
):
    raise NotImplementedError


@router.post(
    "/{category_id}/subcategories",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("category.subcategory.assign"))],
    summary="Добавить подкатегорию (связь категория–подкатегория)",
    responses={
        404: CATEGORY_SUBCATEGORY_404
    }
)
async def add_subcategory_to_category(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1, description="Идентификатор категории")],
    subcategory_id: Annotated[int, Body(ge=1, description="Идентификатор подкатегории")],
):
    raise NotImplementedError


@router.delete(
    "/{category_id}/subcategories/{subcategory_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("category.subcategory.remove"))],
    summary="Удалить связь категория–подкатегория",
    responses={
        404: CATEGORY_SUBCATEGORY_404
    }
)
async def remove_subcategory_from_category(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1, description="Идентификатор категории")],
    subcategory_id: Annotated[int, Path(ge=1, description="Идентификатор подкатегории")],
):
    raise NotImplementedError
