from decimal import ROUND_HALF_UP, Decimal
from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path
from orjson import loads

from core.exceptions import APIException
from core.methods import get_connection, require_permissions
from modules.products.product import repositories
from modules.products.product.responses import (
    MATERIAL_OR_RESOURCE_NOT_FOUND,
    PRODUCT_MATERIAL_SHORTAGE_NOT_FOUND,
    PRODUCT_NOT_FOUND,
    PRODUCT_UPDATE_NOT_FOUND,
)
from modules.products.product.schemes import (
    ProductCreate,
    ProductCreateResponse,
    ProductMaterialShortageLineResponse,
    ProductMaterialShortageRequest,
    ProductMaterialShortageResponse,
    ProductRead,
    ProductUpdate,
)

router = APIRouter()


async def _validate_material_shortage_references(
    connection: Connection,
    payload: ProductMaterialShortageRequest,
) -> None:
    requested_ids = {x.product_id for x in payload.lines}
    found_products = await repositories.fetch_existing_product_ids(connection, list(requested_ids))
    missing_products = sorted(requested_ids - found_products)
    if missing_products:
        raise APIException(
            status_code=404,
            code="PRODUCT_NOT_FOUND",
            message="Продукт не найден",
            details={"product_ids": missing_products},
        )

    wh = payload.warehouse_ids
    if not wh:
        return

    found_wh = await repositories.fetch_existing_warehouse_ids(connection, wh)
    missing_wh = sorted(set(wh) - found_wh)
    if missing_wh:
        raise APIException(
            status_code=404,
            code="WAREHOUSES_NOT_FOUND",
            message="Склад не найден",
            details={"warehouse_ids": missing_wh},
        )


async def _validate_product_references(connection: Connection, payload: ProductCreate | ProductUpdate) -> None:
    material_ids = {payload.output_material.output_material_id, *(m.material_id for m in payload.input_materials)}
    found_materials = await repositories.fetch_existing_material_ids(connection, list(material_ids))

    if material_ids != found_materials:
        raise APIException(
            status_code=404,
            code="MATERIAL_NOT_FOUND",
            message="Материал не найден",
        )

    resource_ids = {r.resource_id for r in payload.input_resources}
    found_resources = await repositories.fetch_existing_resource_ids(connection, list(resource_ids))

    if resource_ids != found_resources:
        raise APIException(
            status_code=404,
            code="RESOURCE_NOT_FOUND",
            message="Ресурс не найден",
        )


@router.post(
    "/",
    response_model=ProductCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions("product.create"))],
    summary="Создать новый продукт",
    responses={
        404: MATERIAL_OR_RESOURCE_NOT_FOUND,
    },
)
async def create_product(
    connection: Annotated[Connection, Depends(get_connection)],
    payload: Annotated[ProductCreate, Body()],
):
    await _validate_product_references(connection, payload)

    async with connection.transaction():
        product_id = await repositories.create_product(connection, payload)

        await repositories.replace_product_materials(
            connection,
            product_id,
            [x.model_dump() for x in payload.input_materials],
        )

        await repositories.replace_product_resources(
            connection,
            product_id,
            [x.model_dump() for x in payload.input_resources],
        )

    return ProductCreateResponse(id=product_id)


@router.post(
    "/shortage",
    response_model=ProductMaterialShortageResponse,
    dependencies=[Depends(require_permissions("product.read"))],
    summary="Проверить нехватку материалов для выпуска",
    responses={
        404: PRODUCT_MATERIAL_SHORTAGE_NOT_FOUND,
    },
)
async def product_material_shortage(
    connection: Annotated[Connection, Depends(get_connection)],
    payload: Annotated[ProductMaterialShortageRequest, Body()],
):
    await _validate_material_shortage_references(connection, payload)

    warehouse_filter = payload.warehouse_ids if payload.warehouse_ids else None
    lines = [(x.product_id, x.quantity) for x in payload.lines]
    rows = await repositories.product_material_shortage_lines(connection, lines, warehouse_filter)

    q = Decimal("0.001")
    shortages: list[ProductMaterialShortageLineResponse] = []
    for pid, s in rows:
        sq = s.quantize(q, rounding=ROUND_HALF_UP)
        if sq > 0:
            shortages.append(ProductMaterialShortageLineResponse(product_id=pid, shortage_quantity=sq))

    return ProductMaterialShortageResponse(shortages=shortages)


@router.get(
    "/{product_id}",
    response_model=ProductRead,
    dependencies=[Depends(require_permissions("product.read"))],
    summary="Получить информацию о продукте",
    responses={
        404: PRODUCT_NOT_FOUND,
    },
)
async def get_product(
    connection: Annotated[Connection, Depends(get_connection)],
    product_id: Annotated[int, Path(ge=1, description="Идентификатор продукта")],
):
    product = await repositories.get_product_by_id(connection, product_id)

    if product is None:
        raise APIException(
            status_code=404,
            code="PRODUCT_NOT_FOUND",
            message="Продукт не найден",
        )

    return ProductRead.model_validate(
        {
            **product,
            "output_material": {
                "id": product["output_material_id"],
                "name": product["output_material_name"],
                "output_quantity": product["output_quantity"],
                "unit": {
                    "id": product["output_material_unit_id"],
                    "name": product["output_material_unit_name"],
                    "short_name": product["output_material_unit_short_name"],
                },
            },
            'input_materials': [loads(x) for x in product['materials']],
            'input_resources': [loads(x) for x in product['resources']],
        }
    )


@router.put(
    "/{product_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("product.update"))],
    summary="Обновить продукт вместе с материалами и ресурсами",
    responses={
        404: PRODUCT_UPDATE_NOT_FOUND,
    },
)
async def update_product(
    connection: Annotated[Connection, Depends(get_connection)],
    product_id: Annotated[int, Path(ge=1, description="Идентификатор продукта")],
    payload: Annotated[ProductUpdate, Body()],
):
    product = await repositories.get_product_by_id(connection, product_id)

    if product is None:
        raise APIException(
            status_code=404,
            code="PRODUCT_NOT_FOUND",
            message="Продукт не найден",
        )

    await _validate_product_references(connection, payload)

    async with connection.transaction():
        await repositories.update_product(connection, product_id, payload)

        await repositories.replace_product_materials(
            connection,
            product_id,
            [x.model_dump() for x in payload.input_materials],
        )

        await repositories.replace_product_resources(
            connection,
            product_id,
            [x.model_dump() for x in payload.input_resources],
        )
