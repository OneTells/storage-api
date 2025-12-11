from typing import Annotated

from fastapi import APIRouter, Body, HTTPException

from core.methods.response import JSONResponse
from core.objects import database
from core.utils.openapi import INTERNAL_ERROR_RESPONSE
from modules.v1.warehouses.schemas import (
    WarehouseCreate, WarehouseCreateResponse, WarehouseIdType, WarehouseRead, WarehouseUpdate
)
from modules.v1.warehouses.warehouse import repositories

WAREHOUSE_NOT_FOUND_RESPONSE = {
    "description": "Склад не существует",
    "content": {
        "application/json": {
            "example": {"detail": "Склад не существует"}
        }
    }
}

router = APIRouter()


@router.post(
    "/",
    response_model=WarehouseCreateResponse,
    status_code=201,
    summary="Создать новый склад",
    responses={
        201: {"description": "Идентификатор созданного склада"},
    }
)
async def create_warehouse(payload: Annotated[WarehouseCreate, Body()]):
    async with database.acquire() as connection:
        warehouse_id = await repositories.create_warehouse(connection, payload)

    return {'id': warehouse_id}


@router.get(
    "/{warehouse_id}",
    response_model=WarehouseRead,
    summary="Получить информацию о складе",
    responses={
        200: {"description": "Информация о складе"},
        404: WAREHOUSE_NOT_FOUND_RESPONSE,
    }
)
async def get_warehouse(warehouse_id: WarehouseIdType):
    async with database.acquire() as connection:
        data = await repositories.get_warehouse_by_id(connection, warehouse_id)

    if data is None:
        raise HTTPException(status_code=404, detail="Склад не существует")

    return JSONResponse(content=data)


@router.put(
    "/{warehouse_id}",
    status_code=204,
    summary="Обновить информацию о складе",
    responses={
        204: {"description": "Склад успешно обновлён"},
        404: WAREHOUSE_NOT_FOUND_RESPONSE,
    }
)
async def update_warehouse(
    warehouse_id: WarehouseIdType,
    payload: Annotated[WarehouseUpdate, Body()]
):
    async with database.acquire() as connection:
        data = await repositories.update_warehouse(connection, warehouse_id, payload)

    if data is None:
        raise HTTPException(status_code=404, detail="Склад не существует")

    return None
