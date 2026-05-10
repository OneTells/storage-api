from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path

from core.exceptions import APIException
from core.methods import get_connection, require_permissions
from modules.materials.material import repositories
from modules.materials.material.responses import MATERIAL_NOT_FOUND, MATERIAL_SKU_CONFLICT, UNIT_NOT_FOUND
from modules.materials.material.schemes import (
    MaterialCreate,
    MaterialCreateResponse,
    MaterialRead,
    MaterialUpdate,
)

router = APIRouter()


@router.post(
    "/",
    response_model=MaterialCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions("material.create"))],
    summary="Создать материал",
    responses={
        404: UNIT_NOT_FOUND,
        409: MATERIAL_SKU_CONFLICT,
    },
)
async def create_material(
    connection: Annotated[Connection, Depends(get_connection)],
    payload: Annotated[MaterialCreate, Body()],
):
    unit_ok = await repositories.exists_unit(connection, payload.unit_id)

    if not unit_ok:
        raise APIException(
            status_code=404,
            code="UNIT_NOT_FOUND",
            message="Единица измерения не найдена",
        )

    sku_taken = await repositories.exists_material_by_sku(connection, payload.sku)

    if sku_taken:
        raise APIException(
            status_code=409,
            code="MATERIAL_SKU_EXISTS",
            message="Материал с таким артикулом уже существует",
        )

    material_id = await repositories.create_material(connection, payload)
    return MaterialCreateResponse(id=material_id)


@router.get(
    "/{material_id}",
    response_model=MaterialRead,
    dependencies=[Depends(require_permissions("material.read"))],
    summary="Получить материал",
    responses={
        404: MATERIAL_NOT_FOUND,
    },
)
async def get_material(
    connection: Annotated[Connection, Depends(get_connection)],
    material_id: Annotated[int, Path(ge=1, description="Идентификатор материала")],
):
    row = await repositories.get_material_by_id(connection, material_id)

    if row is None:
        raise APIException(
            status_code=404,
            code="MATERIAL_NOT_FOUND",
            message="Материал не найден",
        )

    stock_rows = await repositories.fetch_material_warehouse_stocks(connection, material_id)

    return MaterialRead.model_validate(
        {
            **row,
            'warehouse_stocks': [dict(x) for x in stock_rows]
        }
    )


@router.put(
    "/{material_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("material.update"))],
    summary="Обновить материал",
    responses={
        404: MATERIAL_NOT_FOUND,
        409: MATERIAL_SKU_CONFLICT,
    },
)
async def update_material(
    connection: Annotated[Connection, Depends(get_connection)],
    material_id: Annotated[int, Path(ge=1, description="Идентификатор материала")],
    payload: Annotated[MaterialUpdate, Body()],
):
    row = await repositories.get_material_by_id(connection, material_id)

    if row is None:
        raise APIException(
            status_code=404,
            code="MATERIAL_NOT_FOUND",
            message="Материал не найден",
        )

    unit_ok = await repositories.exists_unit(connection, payload.unit_id)

    if not unit_ok:
        raise APIException(
            status_code=404,
            code="UNIT_NOT_FOUND",
            message="Единица измерения не найдена",
        )

    sku_taken = await repositories.exists_material_by_sku(
        connection,
        payload.sku,
        exclude_material_id=material_id,
    )

    if sku_taken:
        raise APIException(
            status_code=409,
            code="MATERIAL_SKU_EXISTS",
            message="Материал с таким артикулом уже существует",
        )

    await repositories.update_material(connection, material_id, payload)
