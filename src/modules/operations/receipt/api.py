from datetime import datetime
from typing import Annotated

from everbase import Connection
from orjson import loads
from fastapi import APIRouter, Body, Depends, Path, Query

from asyncpg import Record
from core.exceptions import APIException
from core.methods import get_connection, get_current_user, require_permissions
from core.models import CounterpartyRoleType, ReceiptStatus
from core.schemes import Pagination, UserModel
from modules.operations.receipt import repositories
from modules.operations.receipt.responses import RECEIPT_404
from modules.operations.receipt.schemes import ReceiptCreate, ReceiptRead, ReceiptsListResponse, ReceiptUpdate
from modules.operations.repositories import counterparty_role_exists, material_exists, warehouse_exists
from modules.operations.exceptions import StockOperationError
from modules.operations.responses import OPERATION_HEADER_NOT_FOUND
from modules.operations.schemes import OperationCreateResponse

router = APIRouter()


def _receipt_read_from_row(row: Record) -> ReceiptRead:
    d = dict(row)
    d["supplier"] = {"id": d.pop("counterparty_id"), "name": d.pop("supplier_name")}
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
    return ReceiptRead.model_validate(d)


@router.get(
    "/receipts",
    response_model=ReceiptsListResponse,
    dependencies=[Depends(require_permissions("operations.receipt.read"))],
    summary="Список приёмок от поставщика",
)
async def fetch_receipts(
    connection: Annotated[Connection, Depends(get_connection)],
    page: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    limit: Annotated[int, Query(ge=1, le=1000, description="Размер страницы")] = 100,
    user_id: Annotated[int | None, Query(ge=1, description="Фильтр по пользователю")] = None,
    created_from: Annotated[datetime | None, Query(description="Начало периода создания операции")] = None,
    created_to: Annotated[datetime | None, Query(description="Конец периода создания операции")] = None,
    status: Annotated[
        ReceiptStatus | None,
        Query(description="Фильтр по статусу приёмки"),
    ] = None,
):
    rows = await repositories.fetch_receipts(connection, page, limit, user_id, created_from, created_to, status)
    total = await repositories.count_receipts(connection, user_id, created_from, created_to, status)

    return ReceiptsListResponse(
        items=[_receipt_read_from_row(x) for x in rows],
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
    "/receipts/{operation_id}",
    response_model=ReceiptRead,
    dependencies=[Depends(require_permissions("operations.receipt.read"))],
    summary="Получить приёмку",
    responses={404: OPERATION_HEADER_NOT_FOUND},
)
async def get_receipt(
    connection: Annotated[Connection, Depends(get_connection)],
    operation_id: Annotated[int, Path(ge=1, description="Идентификатор операции")],
):
    row = await repositories.get_receipt(connection, operation_id)

    if row is None:
        raise APIException(status_code=404, code="OPERATION_NOT_FOUND", message="Операция не найдена")

    return _receipt_read_from_row(row)


@router.post(
    "/receipts",
    response_model=OperationCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions("operations.receipt.create"))],
    summary="Создать приёмку от поставщика",
    responses={
        404: RECEIPT_404,
    },
)
async def create_receipt(
    connection: Annotated[Connection, Depends(get_connection)],
    user: Annotated[UserModel, Depends(get_current_user)],
    payload: Annotated[ReceiptCreate, Body()],
):
    if not payload.items:
        raise APIException(status_code=422, code="EMPTY_ITEMS", message="Список позиций не может быть пустым")

    if not await warehouse_exists(connection, payload.warehouse_id):
        raise APIException(status_code=404, code="WAREHOUSE_NOT_FOUND", message="Склад не найден")

    if not await counterparty_role_exists(connection, payload.supplier_id, CounterpartyRoleType.SUPPLIER):
        raise APIException(status_code=404, code="SUPPLIER_NOT_FOUND", message="Поставщик не найден")

    for it in payload.items:
        if not await material_exists(connection, it.material_id):
            raise APIException(status_code=404, code="MATERIAL_NOT_FOUND", message="Материал не найден")

    op_id = await repositories.create_receipt(connection, user.id, payload)
    return OperationCreateResponse(id=op_id)


@router.patch(
    "/receipts/{operation_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("operations.receipt.update"))],
    summary="Изменить приёмку от поставщика",
    responses={
        404: RECEIPT_404,
    },
)
async def update_receipt(
    connection: Annotated[Connection, Depends(get_connection)],
    operation_id: Annotated[int, Path(ge=1, description="Идентификатор операции")],
    payload: Annotated[ReceiptUpdate, Body()],
):
    row = await repositories.get_receipt(connection, operation_id)

    if row is None:
        raise APIException(status_code=404, code="OPERATION_NOT_FOUND", message="Операция не найдена")

    if payload.warehouse_id is not None:
        if not await warehouse_exists(connection, payload.warehouse_id):
            raise APIException(status_code=404, code="WAREHOUSE_NOT_FOUND", message="Склад не найден")

    if payload.supplier_id is not None:
        if not await counterparty_role_exists(connection, payload.supplier_id, CounterpartyRoleType.SUPPLIER):
            raise APIException(status_code=404, code="SUPPLIER_NOT_FOUND", message="Поставщик не найден")

    if payload.items is not None:
        if not payload.items:
            raise APIException(status_code=422, code="EMPTY_ITEMS", message="Список позиций не может быть пустым")

        for it in payload.items:
            if not await material_exists(connection, it.material_id):
                raise APIException(status_code=404, code="MATERIAL_NOT_FOUND", message="Материал не найден")

    try:
        await repositories.update_receipt(connection, operation_id, payload)
    except StockOperationError as e:
        raise APIException(status_code=422, code=e.code, message=e.message) from e
