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
from modules.operations.write_off_to_production import repositories
from modules.operations.write_off_to_production.responses import WRITE_OFF_TO_PRODUCTION_404
from modules.operations.write_off_to_production.schemes import (
    WriteOffToProductionCreate,
    WriteOffToProductionRead,
    WriteOffToProductionUpdate,
    WriteOffsToProductionListResponse,
)

router = APIRouter()


def _write_off_tp_read_from_row(row: Record) -> WriteOffToProductionRead:
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
    return WriteOffToProductionRead.model_validate(d)


@router.get(
    "/write_offs_to_production",
    response_model=WriteOffsToProductionListResponse,
    dependencies=[Depends(require_permissions("operations.write_off_to_production.read"))],
    summary="Список списаний в производство",
)
async def fetch_write_offs_to_production(
    connection: Annotated[Connection, Depends(get_connection)],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    user_id: Annotated[int | None, Query(ge=1, description="Фильтр по пользователю")] = None,
    created_from: Annotated[datetime | None, Query(description="Начало периода создания операции")] = None,
    created_to: Annotated[datetime | None, Query(description="Конец периода создания операции")] = None,
    status: Annotated[
        OperationStatus | None,
        Query(description="Фильтр по статусу списания в производство"),
    ] = None,
):
    rows = await repositories.fetch_write_offs_to_production(
        connection, page, limit, user_id, created_from, created_to, status
    )
    total = await repositories.count_write_offs_to_production(connection, user_id, created_from, created_to, status)

    return WriteOffsToProductionListResponse(
        items=[_write_off_tp_read_from_row(r) for r in rows],
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
    "/write_offs_to_production/{operation_id}",
    response_model=WriteOffToProductionRead,
    dependencies=[Depends(require_permissions("operations.write_off_to_production.read"))],
    summary="Получить списание в производство",
    responses={404: OPERATION_HEADER_NOT_FOUND},
)
async def get_write_off_to_production(
    connection: Annotated[Connection, Depends(get_connection)],
    operation_id: Annotated[int, Path(ge=1, description="Идентификатор операции")],
):
    row = await repositories.get_write_off_to_production(connection, operation_id)

    if row is None:
        raise APIException(status_code=404, code="OPERATION_NOT_FOUND", message="Операция не найдена")

    return _write_off_tp_read_from_row(row)


@router.post(
    "/write_offs_to_production",
    response_model=OperationCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions("operations.write_off_to_production.create"))],
    summary="Создать списание в производство",
    responses={
        404: WRITE_OFF_TO_PRODUCTION_404,
    },
)
async def create_write_off_to_production(
    connection: Annotated[Connection, Depends(get_connection)],
    user: Annotated[UserModel, Depends(get_current_user)],
    payload: Annotated[WriteOffToProductionCreate, Body()],
):
    if not payload.items:
        raise APIException(status_code=422, code="EMPTY_ITEMS", message="Список позиций не может быть пустым")

    if not await warehouse_exists(connection, payload.warehouse_id):
        raise APIException(status_code=404, code="WAREHOUSE_NOT_FOUND", message="Склад не найден")

    for it in payload.items:
        if not await material_exists(connection, it.material_id):
            raise APIException(status_code=404, code="MATERIAL_NOT_FOUND", message="Материал не найден")

    op_id = await repositories.create_write_off_to_production(connection, user.id, payload)
    return OperationCreateResponse(id=op_id)


@router.patch(
    "/write_offs_to_production/{operation_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("operations.write_off_to_production.update"))],
    summary="Изменить списание в производство",
    responses={
        404: WRITE_OFF_TO_PRODUCTION_404,
    },
)
async def update_write_off_to_production(
    connection: Annotated[Connection, Depends(get_connection)],
    operation_id: Annotated[int, Path(ge=1, description="Идентификатор операции")],
    payload: Annotated[WriteOffToProductionUpdate, Body()],
):
    row = await repositories.get_write_off_to_production(connection, operation_id)

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
        await repositories.update_write_off_to_production(connection, operation_id, payload)
    except StockOperationError as e:
        raise APIException(status_code=422, code=e.code, message=e.message) from e
