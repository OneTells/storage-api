from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path

from core.exceptions import APIException
from core.methods import get_connection, require_permissions
from modules.products.categories.category import repositories
from modules.products.categories.category.responses import (
    PRODUCT_CATEGORY_DELETE_CONFLICT,
    PRODUCT_CATEGORY_NOT_FOUND,
    PRODUCT_CATEGORY_PRODUCT_404,
    PRODUCT_CATEGORY_SUBCATEGORY_404,
    PRODUCT_CATEGORY_SUBCATEGORY_BAD_REQUEST,
)
from modules.products.categories.category.schemes import (
    ProductCategoryCreate,
    ProductCategoryCreateResponse,
    ProductCategoryRead,
    ProductCategoryUpdate,
)

router = APIRouter()


@router.post(
    "/",
    response_model=ProductCategoryCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions("product.category.create"))],
    summary="Создать категорию",
)
async def create_product_category(
    connection: Annotated[Connection, Depends(get_connection)],
    payload: Annotated[ProductCategoryCreate, Body()],
):
    category_id = await repositories.create_product_category(connection, payload)
    return ProductCategoryCreateResponse(id=category_id)


@router.get(
    "/{category_id}",
    response_model=ProductCategoryRead,
    dependencies=[Depends(require_permissions("product.category.read"))],
    summary="Получить категорию",
    responses={404: PRODUCT_CATEGORY_NOT_FOUND},
)
async def get_product_category(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1, description="Идентификатор категории")],
):
    row = await repositories.get_product_category_by_id(connection, category_id)

    if row is None:
        raise APIException(
            status_code=404,
            code="PRODUCT_CATEGORY_NOT_FOUND",
            message="Категория не найдена",
        )

    return ProductCategoryRead.model_validate(dict(row))


@router.put(
    "/{category_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("product.category.update"))],
    summary="Обновить категорию",
    responses={404: PRODUCT_CATEGORY_NOT_FOUND},
)
async def update_product_category(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1, description="Идентификатор категории")],
    payload: Annotated[ProductCategoryUpdate, Body()],
):
    row = await repositories.get_product_category_by_id(connection, category_id)

    if row is None:
        raise APIException(
            status_code=404,
            code="PRODUCT_CATEGORY_NOT_FOUND",
            message="Категория не найдена",
        )

    await repositories.update_product_category(connection, category_id, payload)


@router.delete(
    "/{category_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("product.category.delete"))],
    summary="Удалить категорию",
    responses={
        404: PRODUCT_CATEGORY_NOT_FOUND,
        409: PRODUCT_CATEGORY_DELETE_CONFLICT,
    },
)
async def delete_product_category(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1, description="Идентификатор категории")],
):
    row = await repositories.get_product_category_by_id(connection, category_id)

    if row is None:
        raise APIException(
            status_code=404,
            code="PRODUCT_CATEGORY_NOT_FOUND",
            message="Категория не найдена",
        )

    n_sub = await repositories.count_product_category_subcategories(connection, category_id)
    n_prod = await repositories.count_product_category_products(connection, category_id)

    if n_sub and n_prod:
        raise APIException(
            status_code=409,
            code="PRODUCT_CATEGORY_DELETE_CONFLICT",
            message="Удаление категории невозможно из-за наличия дочерних категорий и продуктов",
        )
    if n_sub:
        raise APIException(
            status_code=409,
            code="PRODUCT_CATEGORY_DELETE_CONFLICT",
            message="Удаление категории невозможно из-за наличия дочерних категорий",
        )
    if n_prod:
        raise APIException(
            status_code=409,
            code="PRODUCT_CATEGORY_DELETE_CONFLICT",
            message="Удаление категории невозможно из-за наличия продуктов в категории",
        )

    await repositories.delete_product_category(connection, category_id)


@router.post(
    "/{category_id}/products/{product_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("product.category.product.assign"))],
    summary="Привязать продукт к категории",
    responses={404: PRODUCT_CATEGORY_PRODUCT_404},
)
async def bind_product_to_category(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1, description="Идентификатор категории")],
    product_id: Annotated[int, Path(ge=1, description="Идентификатор продукта")],
):
    if not await repositories.product_category_exists(connection, category_id):
        raise APIException(
            status_code=404,
            code="PRODUCT_CATEGORY_NOT_FOUND",
            message="Категория не найдена",
        )

    if not await repositories.product_exists(connection, product_id):
        raise APIException(
            status_code=404,
            code="PRODUCT_NOT_FOUND",
            message="Продукт не найден",
        )

    if await repositories.category_product_link_exists(connection, category_id, product_id):
        return None

    await repositories.insert_category_product(connection, category_id, product_id)
    return None


@router.delete(
    "/{category_id}/products/{product_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("product.category.product.remove"))],
    summary="Отвязать продукт от категории",
    responses={404: PRODUCT_CATEGORY_PRODUCT_404},
)
async def unbind_product_from_category(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1, description="Идентификатор категории")],
    product_id: Annotated[int, Path(ge=1, description="Идентификатор продукта")],
):
    if not await repositories.product_category_exists(connection, category_id):
        raise APIException(
            status_code=404,
            code="PRODUCT_CATEGORY_NOT_FOUND",
            message="Категория не найдена",
        )

    if not await repositories.product_exists(connection, product_id):
        raise APIException(
            status_code=404,
            code="PRODUCT_NOT_FOUND",
            message="Продукт не найден",
        )

    if not await repositories.category_product_link_exists(connection, category_id, product_id):
        raise APIException(
            status_code=404,
            code="PRODUCT_CATEGORY_PRODUCT_NOT_LINKED",
            message="Продукт не привязан к этой категории",
        )

    await repositories.delete_category_product(connection, category_id, product_id)


@router.post(
    "/{category_id}/subcategories/{subcategory_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("product.category.subcategory.assign"))],
    summary="Добавить подкатегорию (связь категория–подкатегория)",
    responses={
        400: PRODUCT_CATEGORY_SUBCATEGORY_BAD_REQUEST,
        404: PRODUCT_CATEGORY_SUBCATEGORY_404,
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
            code="PRODUCT_CATEGORY_SUBCATEGORY_SELF",
            message="Нельзя связать категорию саму с собой",
        )

    if not await repositories.product_category_exists(connection, category_id):
        raise APIException(
            status_code=404,
            code="PRODUCT_CATEGORY_NOT_FOUND",
            message="Категория не найдена",
        )

    if not await repositories.product_category_exists(connection, subcategory_id):
        raise APIException(
            status_code=404,
            code="PRODUCT_SUBCATEGORY_NOT_FOUND",
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
    dependencies=[Depends(require_permissions("product.category.subcategory.remove"))],
    summary="Удалить связь категория–подкатегория",
    responses={404: PRODUCT_CATEGORY_SUBCATEGORY_404},
)
async def remove_subcategory_from_category(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1, description="Идентификатор категории")],
    subcategory_id: Annotated[int, Path(ge=1, description="Идентификатор подкатегории")],
):
    if not await repositories.product_category_exists(connection, category_id):
        raise APIException(
            status_code=404,
            code="PRODUCT_CATEGORY_NOT_FOUND",
            message="Категория не найдена",
        )

    if not await repositories.product_category_exists(connection, subcategory_id):
        raise APIException(
            status_code=404,
            code="PRODUCT_SUBCATEGORY_NOT_FOUND",
            message="Подкатегория не найдена",
        )

    if not await repositories.category_subcategory_link_exists(connection, category_id, subcategory_id):
        raise APIException(
            status_code=404,
            code="PRODUCT_CATEGORY_SUBCATEGORY_NOT_LINKED",
            message="Подкатегория не привязана к этой категории",
        )

    await repositories.delete_category_subcategory(connection, category_id, subcategory_id)
