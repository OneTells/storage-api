from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path

from core.exceptions import APIException
from core.methods import get_connection, require_permissions
from modules.materials.categories.category import repositories
from modules.materials.categories.category.responses import (
    CATEGORY_DELETE_CONFLICT,
    CATEGORY_NOT_FOUND,
    CATEGORY_OBJECT_404,
    CATEGORY_SUBCATEGORY_404,
    CATEGORY_SUBCATEGORY_BAD_REQUEST,
)
from modules.materials.categories.category.schemes import CategoryCreate, CategoryCreateResponse, CategoryRead, CategoryUpdate

router = APIRouter()


@router.post(
    "/",
    response_model=CategoryCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions("material.category.create"))],
    summary="Создать категорию",
)
async def create_category(
    connection: Annotated[Connection, Depends(get_connection)],
    payload: Annotated[CategoryCreate, Body()],
):
    category_id = await repositories.create_material_category(connection, payload)
    return CategoryCreateResponse(id=category_id)


@router.get(
    "/{category_id}",
    response_model=CategoryRead,
    dependencies=[Depends(require_permissions("material.category.read"))],
    summary="Получить категорию",
    responses={
        404: CATEGORY_NOT_FOUND,
    },
)
async def get_category(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1, description="Идентификатор категории")],
):
    row = await repositories.get_material_category_by_id(connection, category_id)

    if row is None:
        raise APIException(
            status_code=404,
            code="CATEGORY_NOT_FOUND",
            message="Категория не найдена",
        )

    return CategoryRead(**dict(row))


@router.put(
    "/{category_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("material.category.update"))],
    summary="Обновить категорию",
    responses={
        404: CATEGORY_NOT_FOUND,
    },
)
async def update_category(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1, description="Идентификатор категории")],
    payload: Annotated[CategoryUpdate, Body()],
):
    row = await repositories.get_material_category_by_id(connection, category_id)

    if row is None:
        raise APIException(
            status_code=404,
            code="CATEGORY_NOT_FOUND",
            message="Категория не найдена",
        )

    await repositories.update_material_category(connection, category_id, payload)


@router.delete(
    "/{category_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("material.category.delete"))],
    summary="Удалить категорию",
    responses={
        404: CATEGORY_NOT_FOUND,
        409: CATEGORY_DELETE_CONFLICT,
    },
)
async def delete_category(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1, description="Идентификатор категории")],
):
    row = await repositories.get_material_category_by_id(connection, category_id)

    if row is None:
        raise APIException(
            status_code=404,
            code="CATEGORY_NOT_FOUND",
            message="Категория не найдена",
        )

    n_sub = await repositories.count_material_category_subcategories(connection, category_id)
    n_mat = await repositories.count_material_category_materials(connection, category_id)

    if n_sub and n_mat:
        raise APIException(
            status_code=409,
            code="CATEGORY_DELETE_CONFLICT",
            message="Удаление категории невозможно из-за наличия дочерних категорий и материалов",
        )
    if n_sub:
        raise APIException(
            status_code=409,
            code="CATEGORY_DELETE_CONFLICT",
            message="Удаление категории невозможно из-за наличия дочерних категорий",
        )
    if n_mat:
        raise APIException(
            status_code=409,
            code="CATEGORY_DELETE_CONFLICT",
            message="Удаление категории невозможно из-за наличия дочерних материалов",
        )

    await repositories.delete_material_category(connection, category_id)


@router.post(
    "/{category_id}/materials/{material_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("material.category.material.assign"))],
    summary="Привязать материал к категории",
    responses={
        404: CATEGORY_OBJECT_404,
    },
)
async def bind_material_to_category(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1, description="Идентификатор категории")],
    material_id: Annotated[int, Path(ge=1, description="Идентификатор материала")],
):
    if not await repositories.material_category_exists(connection, category_id):
        raise APIException(
            status_code=404,
            code="CATEGORY_NOT_FOUND",
            message="Категория не найдена",
        )

    if not await repositories.material_exists(connection, material_id):
        raise APIException(
            status_code=404,
            code="MATERIAL_NOT_FOUND",
            message="Материал не найден",
        )

    if await repositories.category_material_link_exists(connection, category_id, material_id):
        return None

    await repositories.insert_category_material(connection, category_id, material_id)
    return None


@router.delete(
    "/{category_id}/materials/{material_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("material.category.material.remove"))],
    summary="Отвязать материал от категории",
    responses={
        404: CATEGORY_OBJECT_404,
    },
)
async def unbind_material_from_category(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1, description="Идентификатор категории")],
    material_id: Annotated[int, Path(ge=1, description="Идентификатор материала")],
):
    if not await repositories.material_category_exists(connection, category_id):
        raise APIException(
            status_code=404,
            code="CATEGORY_NOT_FOUND",
            message="Категория не найдена",
        )

    if not await repositories.material_exists(connection, material_id):
        raise APIException(
            status_code=404,
            code="MATERIAL_NOT_FOUND",
            message="Материал не найден",
        )

    if not await repositories.category_material_link_exists(connection, category_id, material_id):
        raise APIException(
            status_code=404,
            code="CATEGORY_MATERIAL_NOT_LINKED",
            message="Материал не привязан к этой категории",
        )

    await repositories.delete_category_material(connection, category_id, material_id)


@router.post(
    "/{category_id}/subcategories/{subcategory_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("material.category.subcategory.assign"))],
    summary="Добавить подкатегорию (связь категория–подкатегория)",
    responses={
        400: CATEGORY_SUBCATEGORY_BAD_REQUEST,
        404: CATEGORY_SUBCATEGORY_404,
    },
)
async def add_subcategory_to_category(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1, description="Идентификатор категории")],
    subcategory_id: Annotated[int, Path(ge=1, description="Идентификатор подкатегории")],
):
    if category_id == subcategory_id:
        raise APIException(
            status_code=400,
            code="CATEGORY_SUBCATEGORY_SELF",
            message="Нельзя связать категорию саму с собой",
        )

    if not await repositories.material_category_exists(connection, category_id):
        raise APIException(
            status_code=404,
            code="CATEGORY_NOT_FOUND",
            message="Категория не найдена",
        )

    if not await repositories.material_category_exists(connection, subcategory_id):
        raise APIException(
            status_code=404,
            code="SUBCATEGORY_NOT_FOUND",
            message="Подкатегория не найдена",
        )

    if await repositories.category_subcategory_link_exists(connection, category_id, subcategory_id):
        return None

    await repositories.insert_category_subcategory(connection, category_id, subcategory_id)
    return None


@router.delete(
    "/{category_id}/subcategories/{subcategory_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("material.category.subcategory.remove"))],
    summary="Удалить связь категория–подкатегория",
    responses={
        404: CATEGORY_SUBCATEGORY_404,
    },
)
async def remove_subcategory_from_category(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1, description="Идентификатор категории")],
    subcategory_id: Annotated[int, Path(ge=1, description="Идентификатор подкатегории")],
):
    if not await repositories.material_category_exists(connection, category_id):
        raise APIException(
            status_code=404,
            code="CATEGORY_NOT_FOUND",
            message="Категория не найдена",
        )

    if not await repositories.material_category_exists(connection, subcategory_id):
        raise APIException(
            status_code=404,
            code="SUBCATEGORY_NOT_FOUND",
            message="Подкатегория не найдена",
        )

    if not await repositories.category_subcategory_link_exists(connection, category_id, subcategory_id):
        raise APIException(
            status_code=404,
            code="CATEGORY_SUBCATEGORY_NOT_LINKED",
            message="Подкатегория не привязана к этой категории",
        )

    await repositories.delete_category_subcategory(connection, category_id, subcategory_id)
