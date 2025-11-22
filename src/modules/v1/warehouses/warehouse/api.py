from typing import Annotated

from asyncpg import Record
from everbase import Insert, Select, Update
from fastapi import APIRouter, Path, HTTPException

from core.models import Warehouse
from core.objects import database
from core.utils.openapi import INTERNAL_ERROR_RESPONSE
from modules.v1.warehouses.schemes import (
    WarehouseCreate,
    WarehouseCreateResponse,
    WarehouseRead,
    WarehouseUpdate
)

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
        500: INTERNAL_ERROR_RESPONSE,
    }
)
async def create_warehouse(payload: WarehouseCreate):
    async with database.get_connection() as connection:
        response: Record = await (
            Insert(Warehouse)
            .values(**payload.model_dump())
            .returning(Warehouse.id)
            .fetch_one(connection)
        )

    return {'id': response['id']}


@router.get(
    "/{warehouse_id}",
    response_model=WarehouseRead,
    summary="Получить информацию о складе",
    responses={
        200: {"description": "Информация о складе"},
        404: WAREHOUSE_NOT_FOUND_RESPONSE,
        500: INTERNAL_ERROR_RESPONSE,
    }
)
async def get_warehouse(
    warehouse_id: Annotated[int, Path(ge=1, description="Идентификатор склада")],
):
    async with database.get_connection() as connection:
        response = await (
            Select(
                Warehouse.id,
                Warehouse.name,
                Warehouse.address,
                Warehouse.is_active,
                Warehouse.created_at
            )
            .where(Warehouse.id == warehouse_id)
            .fetch_one(connection, model=lambda x: dict(x))
        )

    if response is None:
        raise HTTPException(status_code=404, detail="Склад не существует")

    return response


@router.put(
    "/{warehouse_id}",
    status_code=204,
    summary="Обновить информацию о складе",
    responses={
        204: {"description": "Склад успешно обновлён"},
        404: WAREHOUSE_NOT_FOUND_RESPONSE,
        500: INTERNAL_ERROR_RESPONSE,
    }
)
async def update_warehouse(
    warehouse_id: Annotated[int, Path(ge=1, description="Идентификатор склада")],
    payload: WarehouseUpdate,
):
    async with database.get_connection() as connection:
        response = await (
            Update(Warehouse)
            .values(**payload.model_dump())
            .where(Warehouse.id == warehouse_id)
            .returning(Warehouse.id)
            .fetch_one(connection)
        )

    if response is None:
        raise HTTPException(status_code=404, detail="Склад не существует")

    return None
