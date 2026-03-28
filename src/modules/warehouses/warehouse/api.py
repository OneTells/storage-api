from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, HTTPException, Path

from core.methods import get_connection, require_permissions
from core.schemes import ErrorResponse
from modules.warehouses.schemes import WarehouseRead
from modules.warehouses.warehouse import repositories
from modules.warehouses.warehouse.schemes import WarehouseCreate, WarehouseCreateResponse, WarehouseUpdate

WAREHOUSE_NOT_FOUND_RESPONSE = {
    "description": "Склад не найден",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {"detail": "Склад не найден"}
        }
    }
}

router = APIRouter()


@router.post(
    "/",
    response_model=WarehouseCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions('warehouse.create'))],
    summary="Создать новый склад",
    responses={
        201: {"description": "Склад успешно создан"},
    }
)
async def create_warehouse(
    connection: Annotated[Connection, Depends(get_connection)],
    payload: Annotated[WarehouseCreate, Body()]
):
    warehouse_id = await repositories.create_warehouse(connection, payload)
    return WarehouseCreateResponse(id=warehouse_id)


@router.get(
    "/{warehouse_id}",
    response_model=WarehouseRead,
    dependencies=[Depends(require_permissions('warehouse.read'))],
    summary="Получить информацию о складе",
    responses={
        200: {"description": "Информация о складе успешно получена"},
        404: WAREHOUSE_NOT_FOUND_RESPONSE,
    }
)
async def get_warehouse(
    connection: Annotated[Connection, Depends(get_connection)],
    warehouse_id: Annotated[int, Path(ge=1, description="Идентификатор склада")]
):
    warehouse = await repositories.get_warehouse_by_id(connection, warehouse_id)

    if warehouse is None:
        raise HTTPException(status_code=404, detail="Склад не найден")

    return warehouse


@router.put(
    "/{warehouse_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('warehouse.update'))],
    summary="Обновить информацию о складе",
    responses={
        204: {"description": "Склад успешно обновлён"},
        404: WAREHOUSE_NOT_FOUND_RESPONSE,
    }
)
async def update_warehouse(
    connection: Annotated[Connection, Depends(get_connection)],
    warehouse_id: Annotated[int, Path(ge=1, description="Идентификатор склада")],
    payload: Annotated[WarehouseUpdate, Body()]
):
    data = await repositories.update_warehouse(connection, warehouse_id, payload)

    if data is None:
        raise HTTPException(status_code=404, detail="Склад не найден")

    return None
