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
from modules.operations.repositories import material_exists, warehouse_exists
from modules.operations.exceptions import StockOperationError
from modules.operations.responses import OPERATION_HEADER_NOT_FOUND
from modules.operations.schemes import OperationCreateResponse
from modules.operations.transfer import repositories
from modules.operations.transfer.responses import TRANSFER_404
from modules.operations.transfer.schemes import TransferCreate, TransferRead, TransferUpdate, TransfersListResponse

router = APIRouter()


def _transfer_read_from_row(row: Record) -> TransferRead:
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
    return TransferRead.model_validate(d)


@router.get(
    "/transfers",
    response_model=TransfersListResponse,
    dependencies=[Depends(require_permissions("operations.transfer.read"))],
    summary="Список перемещений",
)
async def fetch_transfers(
    connection: Annotated[Connection, Depends(get_connection)],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    user_id: Annotated[int | None, Query(ge=1, description="Фильтр по пользователю")] = None,
    created_from: Annotated[datetime | None, Query(description="Начало периода создания операции")] = None,
    created_to: Annotated[datetime | None, Query(description="Конец периода создания операции")] = None,
    status: Annotated[
        OperationStatus | None,
        Query(description="Фильтр по статусу перемещения"),
    ] = None,
):
    rows = await repositories.fetch_transfers(connection, page, limit, user_id, created_from, created_to, status)
    total = await repositories.count_transfers(connection, user_id, created_from, created_to, status)

    return TransfersListResponse(
        items=[_transfer_read_from_row(r) for r in rows],
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
    "/transfers/{operation_id}",
    response_model=TransferRead,
    dependencies=[Depends(require_permissions("operations.transfer.read"))],
    summary="Получить перемещение",
    responses={404: OPERATION_HEADER_NOT_FOUND},
)
async def get_transfer(
    connection: Annotated[Connection, Depends(get_connection)],
    operation_id: Annotated[int, Path(ge=1, description="Идентификатор операции")],
):
    row = await repositories.get_transfer(connection, operation_id)

    if row is None:
        raise APIException(status_code=404, code="OPERATION_NOT_FOUND", message="Операция не найдена")

    return _transfer_read_from_row(row)


@router.post(
    "/transfers",
    response_model=OperationCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions("operations.transfer.create"))],
    summary="Создать перемещение",
    responses={404: TRANSFER_404},
)
async def create_transfer(
    connection: Annotated[Connection, Depends(get_connection)],
    user: Annotated[UserModel, Depends(get_current_user)],
    payload: Annotated[TransferCreate, Body()],
):
    if payload.from_warehouse_id == payload.to_warehouse_id:
        raise APIException(
            status_code=422,
            code="TRANSFER_WAREHOUSES_MUST_DIFFER",
            message="Склад отправления и склад назначения должны различаться",
        )

    if not payload.items:
        raise APIException(status_code=422, code="EMPTY_ITEMS", message="Список позиций не может быть пустым")

    if not await warehouse_exists(connection, payload.from_warehouse_id):
        raise APIException(status_code=404, code="WAREHOUSE_NOT_FOUND", message="Склад не найден")

    if not await warehouse_exists(connection, payload.to_warehouse_id):
        raise APIException(status_code=404, code="WAREHOUSE_NOT_FOUND", message="Склад не найден")

    for it in payload.items:
        if not await material_exists(connection, it.material_id):
            raise APIException(status_code=404, code="MATERIAL_NOT_FOUND", message="Материал не найден")

    op_id = await repositories.create_transfer(connection, user.id, payload)
    return OperationCreateResponse(id=op_id)


@router.patch(
    "/transfers/{operation_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("operations.transfer.update"))],
    summary="Изменить перемещение",
    responses={404: TRANSFER_404},
)
async def update_transfer(
    connection: Annotated[Connection, Depends(get_connection)],
    operation_id: Annotated[int, Path(ge=1, description="Идентификатор операции")],
    payload: Annotated[TransferUpdate, Body()],
):
    row = await repositories.get_transfer(connection, operation_id)

    if row is None:
        raise APIException(status_code=404, code="OPERATION_NOT_FOUND", message="Операция не найдена")

    fw = int(row["from_warehouse_id"]) if payload.from_warehouse_id is None else payload.from_warehouse_id
    tw = int(row["to_warehouse_id"]) if payload.to_warehouse_id is None else payload.to_warehouse_id

    if payload.from_warehouse_id is not None:
        if not await warehouse_exists(connection, payload.from_warehouse_id):
            raise APIException(status_code=404, code="WAREHOUSE_NOT_FOUND", message="Склад не найден")

    if payload.to_warehouse_id is not None:
        if not await warehouse_exists(connection, payload.to_warehouse_id):
            raise APIException(status_code=404, code="WAREHOUSE_NOT_FOUND", message="Склад не найден")

    if fw == tw:
        raise APIException(
            status_code=422,
            code="TRANSFER_WAREHOUSES_MUST_DIFFER",
            message="Склад отправления и склад назначения должны различаться",
        )

    if payload.items is not None:
        if not payload.items:
            raise APIException(status_code=422, code="EMPTY_ITEMS", message="Список позиций не может быть пустым")

        for it in payload.items:
            if not await material_exists(connection, it.material_id):
                raise APIException(status_code=404, code="MATERIAL_NOT_FOUND", message="Материал не найден")

    try:
        await repositories.update_transfer(connection, operation_id, payload)
    except StockOperationError as e:
        raise APIException(status_code=422, code=e.code, message=e.message) from e
