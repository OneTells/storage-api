from datetime import datetime
from typing import Annotated

from asyncpg import Record
from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path, Query
from orjson import loads

from core.exceptions import APIException
from core.methods import get_connection, get_current_user, require_permissions
from core.models import CounterpartyRoleType, OperationStatus
from core.schemes import Pagination, UserModel
from modules.operations.repositories import counterparty_role_exists, material_exists, warehouse_exists
from modules.operations.exceptions import StockOperationError
from modules.operations.responses import OPERATION_HEADER_NOT_FOUND
from modules.operations.schemes import OperationCreateResponse
from modules.operations.shipment import repositories
from modules.operations.shipment.responses import SHIPMENT_404
from modules.operations.shipment.schemes import ShipmentCreate, ShipmentRead, ShipmentsListResponse, ShipmentUpdate

router = APIRouter()


def _shipment_read_from_row(row: Record) -> ShipmentRead:
    d = dict(row)
    d["customer"] = {"id": d.pop("counterparty_id"), "name": d.pop("customer_name")}
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
    return ShipmentRead.model_validate(d)


@router.get(
    "/shipments",
    response_model=ShipmentsListResponse,
    dependencies=[Depends(require_permissions("operations.shipment.read"))],
    summary="Список отгрузок",
)
async def fetch_shipments(
    connection: Annotated[Connection, Depends(get_connection)],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    user_id: Annotated[int | None, Query(ge=1, description="Фильтр по пользователю")] = None,
    created_from: Annotated[datetime | None, Query(description="Начало периода создания операции")] = None,
    created_to: Annotated[datetime | None, Query(description="Конец периода создания операции")] = None,
    status: Annotated[
        OperationStatus | None,
        Query(description="Фильтр по статусу отгрузки"),
    ] = None,
):
    rows = await repositories.fetch_shipments(connection, page, limit, user_id, created_from, created_to, status)
    total = await repositories.count_shipments(connection, user_id, created_from, created_to, status)

    return ShipmentsListResponse(
        items=[_shipment_read_from_row(r) for r in rows],
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
    "/shipments/{operation_id}",
    response_model=ShipmentRead,
    dependencies=[Depends(require_permissions("operations.shipment.read"))],
    summary="Получить отгрузку",
    responses={404: OPERATION_HEADER_NOT_FOUND},
)
async def get_shipment(
    connection: Annotated[Connection, Depends(get_connection)],
    operation_id: Annotated[int, Path(ge=1, description="Идентификатор операции")],
):
    row = await repositories.get_shipment(connection, operation_id)

    if row is None:
        raise APIException(status_code=404, code="OPERATION_NOT_FOUND", message="Операция не найдена")

    return _shipment_read_from_row(row)


@router.post(
    "/shipments",
    response_model=OperationCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions("operations.shipment.create"))],
    summary="Создать отгрузку",
    responses={
        404: SHIPMENT_404,
    },
)
async def create_shipment(
    connection: Annotated[Connection, Depends(get_connection)],
    user: Annotated[UserModel, Depends(get_current_user)],
    payload: Annotated[ShipmentCreate, Body()],
):
    if not payload.items:
        raise APIException(status_code=422, code="EMPTY_ITEMS", message="Список позиций не может быть пустым")

    if not await warehouse_exists(connection, payload.warehouse_id):
        raise APIException(status_code=404, code="WAREHOUSE_NOT_FOUND", message="Склад не найден")

    if not await counterparty_role_exists(connection, payload.customer_id, CounterpartyRoleType.CUSTOMER):
        raise APIException(status_code=404, code="CUSTOMER_NOT_FOUND", message="Клиент не найден")

    for it in payload.items:
        if not await material_exists(connection, it.material_id):
            raise APIException(status_code=404, code="MATERIAL_NOT_FOUND", message="Материал не найден")

    op_id = await repositories.create_shipment(connection, user.id, payload)
    return OperationCreateResponse(id=op_id)


@router.patch(
    "/shipments/{operation_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("operations.shipment.update"))],
    summary="Изменить отгрузку",
    responses={
        404: SHIPMENT_404,
    },
)
async def update_shipment(
    connection: Annotated[Connection, Depends(get_connection)],
    operation_id: Annotated[int, Path(ge=1, description="Идентификатор операции")],
    payload: Annotated[ShipmentUpdate, Body()],
):
    row = await repositories.get_shipment(connection, operation_id)

    if row is None:
        raise APIException(status_code=404, code="OPERATION_NOT_FOUND", message="Операция не найдена")

    if payload.warehouse_id is not None:
        if not await warehouse_exists(connection, payload.warehouse_id):
            raise APIException(status_code=404, code="WAREHOUSE_NOT_FOUND", message="Склад не найден")

    if payload.customer_id is not None:
        if not await counterparty_role_exists(connection, payload.customer_id, CounterpartyRoleType.CUSTOMER):
            raise APIException(status_code=404, code="CUSTOMER_NOT_FOUND", message="Клиент не найден")

    if payload.items is not None:
        if not payload.items:
            raise APIException(status_code=422, code="EMPTY_ITEMS", message="Список позиций не может быть пустым")

        for it in payload.items:
            if not await material_exists(connection, it.material_id):
                raise APIException(status_code=404, code="MATERIAL_NOT_FOUND", message="Материал не найден")

    try:
        await repositories.update_shipment(connection, operation_id, payload)
    except StockOperationError as e:
        raise APIException(status_code=422, code=e.code, message=e.message) from e
