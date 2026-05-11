from datetime import datetime
from typing import Annotated

from asyncpg import Record
from orjson import loads
from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path, Query

from core.exceptions import APIException
from core.methods import get_connection, get_current_user, require_permissions
from core.models import ReservationStatus
from core.schemes import Pagination, UserModel
from modules.operations.repositories import (
    fetch_batch_mv,
    find_fifo_batch_covering_quantity,
    material_exists,
    warehouse_exists,
)
from modules.operations.reservation import repositories
from modules.operations.reservation.responses import RESERVATION_404
from modules.operations.reservation.schemes import (
    ReservationCreate, ReservationRead, ReservationsListResponse, ReservationUpdate
)
from modules.operations.responses import OPERATION_HEADER_NOT_FOUND
from modules.operations.exceptions import StockOperationError
from modules.operations.schemes import OperationCreateResponse

router = APIRouter()


def _reservation_read_from_row(row: Record) -> ReservationRead:
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
    return ReservationRead.model_validate(d)


@router.get(
    "/reservations",
    response_model=ReservationsListResponse,
    dependencies=[Depends(require_permissions("operations.reservation.read"))],
    summary="Список резервирований",
)
async def fetch_reservations(
    connection: Annotated[Connection, Depends(get_connection)],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    user_id: Annotated[int | None, Query(ge=1, description="Фильтр по пользователю")] = None,
    created_from: Annotated[datetime | None, Query(description="Начало периода создания операции")] = None,
    created_to: Annotated[datetime | None, Query(description="Конец периода создания операции")] = None,
    status: Annotated[
        ReservationStatus | None,
        Query(description="Фильтр по статусу резерва"),
    ] = None,
):
    rows = await repositories.fetch_reservations(connection, page, limit, user_id, created_from, created_to, status)
    total = await repositories.count_reservations(connection, user_id, created_from, created_to, status)

    return ReservationsListResponse(
        items=[_reservation_read_from_row(r) for r in rows],
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
    "/reservations/{operation_id}",
    response_model=ReservationRead,
    dependencies=[Depends(require_permissions("operations.reservation.read"))],
    summary="Получить резервирование",
    responses={404: OPERATION_HEADER_NOT_FOUND},
)
async def get_reservation(
    connection: Annotated[Connection, Depends(get_connection)],
    operation_id: Annotated[int, Path(ge=1, description="Идентификатор операции")],
):
    row = await repositories.get_reservation(connection, operation_id)

    if row is None:
        raise APIException(status_code=404, code="OPERATION_NOT_FOUND", message="Операция не найдена")

    return _reservation_read_from_row(row)


@router.post(
    "/reservations",
    response_model=OperationCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions("operations.reservation.create"))],
    summary="Создать резервирование",
    responses={
        404: RESERVATION_404,
    },
)
async def create_reservation(
    connection: Annotated[Connection, Depends(get_connection)],
    user: Annotated[UserModel, Depends(get_current_user)],
    payload: Annotated[ReservationCreate, Body()],
):
    line = payload.items[0]

    if not await warehouse_exists(connection, payload.warehouse_id):
        raise APIException(status_code=404, code="WAREHOUSE_NOT_FOUND", message="Склад не найден")

    if not await material_exists(connection, line.material_id):
        raise APIException(status_code=404, code="MATERIAL_NOT_FOUND", message="Материал не найден")

    fifo = await find_fifo_batch_covering_quantity(
        connection, payload.warehouse_id, line.material_id, line.quantity
    )

    if fifo is None:
        raise APIException(
            status_code=422,
            code="INSUFFICIENT_STOCK_FIFO",
            message="Нет партии с достаточным свободным остатком для резерва по FIFO на указанном складе",
        )

    try:
        op_id = await repositories.create_reservation(connection, user.id, payload, fifo_batch_id=int(fifo["id"]))
    except StockOperationError as e:
        raise APIException(status_code=422, code=e.code, message=e.message) from e
    return OperationCreateResponse(id=op_id, status=payload.status)


@router.patch(
    "/reservations/{operation_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("operations.reservation.update"))],
    summary="Изменить резервирование",
    responses={
        404: RESERVATION_404,
    },
)
async def update_reservation(
    connection: Annotated[Connection, Depends(get_connection)],
    operation_id: Annotated[int, Path(ge=1, description="Идентификатор операции")],
    payload: Annotated[ReservationUpdate, Body()],
):
    row = await repositories.get_reservation(connection, operation_id)

    if row is None:
        raise APIException(status_code=404, code="OPERATION_NOT_FOUND", message="Операция не найдена")

    if payload.quantity is not None:
        next_qty = payload.quantity
        b = await fetch_batch_mv(connection, int(row["batch_id"]))

        if b is None:
            raise APIException(status_code=404, code="BATCH_NOT_FOUND", message="Партия не найдена")

        if b["remaining"] < next_qty:
            raise APIException(
                status_code=404,
                code="INSUFFICIENT_BATCH_QUANTITY",
                message="Недостаточно остатка в партии",
            )

    try:
        await repositories.update_reservation(connection, operation_id, payload)
    except StockOperationError as e:
        raise APIException(status_code=422, code=e.code, message=e.message) from e
