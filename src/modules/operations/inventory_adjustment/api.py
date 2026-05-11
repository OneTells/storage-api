from datetime import datetime
from typing import Annotated

from asyncpg import Record
from orjson import loads
from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path, Query

from core.exceptions import APIException
from core.methods import get_connection, get_current_user, require_permissions
from core.models import OperationStatus
from core.schemes import Pagination, UserModel
from modules.operations.inventory_adjustment import repositories
from modules.operations.inventory_adjustment.responses import INVENTORY_ADJUSTMENT_404
from modules.operations.inventory_adjustment.schemes import (
    InventoryAdjustmentCreate, InventoryAdjustmentRead, InventoryAdjustmentsListResponse, InventoryAdjustmentUpdate
)
from modules.operations.repositories import InsufficientBatchesForFifoError, material_exists, warehouse_exists
from modules.operations.exceptions import StockOperationError
from modules.operations.responses import OPERATION_HEADER_NOT_FOUND
from modules.operations.schemes import OperationCreateResponse

router = APIRouter()


def _inv_adj_read_from_row(row: Record) -> InventoryAdjustmentRead:
    d = dict(row)
    d["created_by"] = {"id": d.pop("created_by_id"), "name": d.pop("created_by_user_name")}
    _items_raw = d.pop("items")
    if _items_raw is None:
        d["items"] = []
    elif isinstance(_items_raw, list):
        d["items"] = _items_raw
    elif isinstance(_items_raw, str):
        _parsed = loads(_items_raw)
        d["items"] = _parsed if isinstance(_parsed, list) else []
    else:
        d["items"] = list(_items_raw)
    return InventoryAdjustmentRead.model_validate(d)


@router.get(
    "/inventory_adjustments",
    response_model=InventoryAdjustmentsListResponse,
    dependencies=[Depends(require_permissions("operations.inventory_adjustment.read"))],
    summary="Список инвентаризаций",
)
async def fetch_inventory_adjustments(
    connection: Annotated[Connection, Depends(get_connection)],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    user_id: Annotated[int | None, Query(ge=1, description="Фильтр по пользователю")] = None,
    created_from: Annotated[datetime | None, Query(description="Начало периода создания операции")] = None,
    created_to: Annotated[datetime | None, Query(description="Конец периода создания операции")] = None,
    status: Annotated[
        OperationStatus | None,
        Query(description="Фильтр по статусу инвентаризации"),
    ] = None,
):
    rows = await repositories.fetch_inventory_adjustments(
        connection, page, limit, user_id, created_from, created_to, status
    )
    total = await repositories.count_inventory_adjustments(connection, user_id, created_from, created_to, status)

    return InventoryAdjustmentsListResponse(
        items=[_inv_adj_read_from_row(x) for x in rows],
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            pages=(total + limit - 1) // limit if total else 0,
            has_next=page * limit < total if total else False,
            has_prev=page > 1 if total else False,
        ),
    )


@router.get(
    "/inventory_adjustments/{operation_id}",
    response_model=InventoryAdjustmentRead,
    dependencies=[Depends(require_permissions("operations.inventory_adjustment.read"))],
    summary="Получить инвентаризацию",
    responses={404: OPERATION_HEADER_NOT_FOUND},
)
async def get_inventory_adjustment(
    connection: Annotated[Connection, Depends(get_connection)],
    operation_id: Annotated[int, Path(ge=1, description="Идентификатор операции")],
):
    row = await repositories.get_inventory_adjustment(connection, operation_id)

    if row is None:
        raise APIException(status_code=404, code="OPERATION_NOT_FOUND", message="Операция не найдена")

    return _inv_adj_read_from_row(row)


@router.post(
    "/inventory_adjustments",
    response_model=OperationCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions("operations.inventory_adjustment.create"))],
    summary="Создать инвентаризацию",
    responses={
        404: INVENTORY_ADJUSTMENT_404,
    },
)
async def create_inventory_adjustment(
    connection: Annotated[Connection, Depends(get_connection)],
    user: Annotated[UserModel, Depends(get_current_user)],
    payload: Annotated[InventoryAdjustmentCreate, Body()],
):
    if not payload.items:
        raise APIException(status_code=422, code="EMPTY_ITEMS", message="Список позиций не может быть пустым")

    if not await warehouse_exists(connection, payload.warehouse_id):
        raise APIException(status_code=404, code="WAREHOUSE_NOT_FOUND", message="Склад не найден")

    for it in payload.items:
        if not await material_exists(connection, it.material_id):
            raise APIException(status_code=404, code="MATERIAL_NOT_FOUND", message="Материал не найден")

    op_id = await repositories.create_inventory_adjustment(connection, user.id, payload)
    return OperationCreateResponse(id=op_id)


@router.patch(
    "/inventory_adjustments/{operation_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("operations.inventory_adjustment.update"))],
    summary="Изменить инвентаризацию",
    responses={
        404: INVENTORY_ADJUSTMENT_404,
    },
)
async def update_inventory_adjustment(
    connection: Annotated[Connection, Depends(get_connection)],
    operation_id: Annotated[int, Path(ge=1, description="Идентификатор операции")],
    payload: Annotated[InventoryAdjustmentUpdate, Body()],
):
    row = await repositories.get_inventory_adjustment(connection, operation_id)

    if row is None:
        raise APIException(status_code=404, code="OPERATION_NOT_FOUND", message="Операция не найдена")

    if payload.warehouse_id is not None:
        if not await warehouse_exists(connection, payload.warehouse_id):
            raise APIException(status_code=404, code="WAREHOUSE_NOT_FOUND", message="Склад не найден")

    if payload.items is not None:
        if not payload.items:
            raise APIException(status_code=422, code="EMPTY_ITEMS", message="Список позиций не может быть пустым")

        for it in payload.items:
            if not await material_exists(connection, it.material_id):
                raise APIException(status_code=404, code="MATERIAL_NOT_FOUND", message="Материал не найден")

    try:
        await repositories.update_inventory_adjustment(connection, operation_id, payload)
    except StockOperationError as e:
        raise APIException(status_code=422, code=e.code, message=e.message) from e
    except InsufficientBatchesForFifoError:
        raise APIException(
            status_code=422,
            code="INVENTORY_ADJUSTMENT_FIFO_NO_BATCH",
            message="Нет партий материала на складе для распределения фактического количества по FIFO",
        ) from None
