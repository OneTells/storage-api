from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path

from core.exceptions import APIException
from core.methods import get_connection, require_permissions
from modules.warehouses.schemes import WarehouseRead
from modules.warehouses.warehouse import repositories
from modules.warehouses.warehouse.responses import WAREHOUSE_NAME_CONFLICT, WAREHOUSE_NOT_FOUND
from modules.warehouses.warehouse.schemes import WarehouseCreate, WarehouseCreateResponse, WarehouseUpdate

router = APIRouter()


@router.post(
    "/",
    response_model=WarehouseCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions('warehouse.create'))],
    summary="Создать новый склад",
    responses={
        409: WAREHOUSE_NAME_CONFLICT
    }
)
async def create_warehouse(
    connection: Annotated[Connection, Depends(get_connection)],
    payload: Annotated[WarehouseCreate, Body()]
):
    warehouse_exists = await repositories.exist_warehouse_by_name(connection, payload.name)

    if warehouse_exists:
        raise APIException(
            status_code=409,
            code="WAREHOUSE_NAME_EXISTS",
            message="Склад с таким названием уже существует"
        )

    warehouse_id = await repositories.create_warehouse(connection, payload)
    return WarehouseCreateResponse(id=warehouse_id)


@router.get(
    "/{warehouse_id}",
    response_model=WarehouseRead,
    dependencies=[Depends(require_permissions('warehouse.read'))],
    summary="Получить информацию о складе",
    responses={
        404: WAREHOUSE_NOT_FOUND,
    }
)
async def get_warehouse(
    connection: Annotated[Connection, Depends(get_connection)],
    warehouse_id: Annotated[int, Path(ge=1, description="Идентификатор склада")]
):
    warehouse = await repositories.get_warehouse_by_id(connection, warehouse_id)

    if warehouse is None:
        raise APIException(
            status_code=404,
            code="WAREHOUSE_NOT_FOUND",
            message="Склад не найден"
        )

    return WarehouseRead(**warehouse)


@router.put(
    "/{warehouse_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('warehouse.update'))],
    summary="Обновить информацию о складе",
    responses={
        404: WAREHOUSE_NOT_FOUND,
        409: WAREHOUSE_NAME_CONFLICT,
    }
)
async def update_warehouse(
    connection: Annotated[Connection, Depends(get_connection)],
    warehouse_id: Annotated[int, Path(ge=1, description="Идентификатор склада")],
    payload: Annotated[WarehouseUpdate, Body()]
):
    warehouse = await repositories.get_warehouse_by_id(connection, warehouse_id)

    if warehouse is None:
        raise APIException(
            status_code=404,
            code="WAREHOUSE_NOT_FOUND",
            message="Склад не найден"
        )

    if warehouse['name'] != payload.name:
        duplicated_name = await repositories.exist_warehouse_by_name(connection, payload.name)

        if duplicated_name:
            raise APIException(
                status_code=409,
                code="WAREHOUSE_NAME_EXISTS",
                message="Склад с таким названием уже существует"
            )

    await repositories.update_warehouse(connection, warehouse_id, payload)
