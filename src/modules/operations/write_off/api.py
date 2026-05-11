from datetime import datetime
from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path, Query

from core.exceptions import APIException
from core.methods import get_connection, get_current_user, require_permissions
from core.schemes import Pagination, UserModel
from modules.operations.repositories import material_exists, warehouse_exists
from modules.operations.responses import OPERATION_HEADER_NOT_FOUND
from modules.operations.schemes import OperationCreateResponse
from modules.operations.write_off import repositories
from modules.operations.write_off.responses import WRITE_OFF_404
from modules.operations.write_off.schemes import WriteOffCreate, WriteOffRead, WriteOffUpdate, WriteOffsListResponse

router = APIRouter()


@router.get(
    "/write_offs",
    response_model=WriteOffsListResponse,
    dependencies=[Depends(require_permissions("operations.write_off.read"))],
    summary="Список прочих списаний",
)
async def fetch_write_offs(
    connection: Annotated[Connection, Depends(get_connection)],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    user_id: Annotated[int | None, Query(ge=1, description="Фильтр по пользователю")] = None,
    created_from: Annotated[datetime | None, Query(description="Начало периода создания операции")] = None,
    created_to: Annotated[datetime | None, Query(description="Конец периода создания операции")] = None,
):
    rows = await repositories.fetch_write_offs(connection, page, limit, user_id, created_from, created_to)
    total = await repositories.count_write_offs(connection, user_id, created_from, created_to)

    return WriteOffsListResponse(
        items=[WriteOffRead.model_validate(dict(r)) for r in rows],
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
    "/write_offs/{operation_id}",
    response_model=WriteOffRead,
    dependencies=[Depends(require_permissions("operations.write_off.read"))],
    summary="Получить прочее списание",
    responses={404: OPERATION_HEADER_NOT_FOUND},
)
async def get_write_off(
    connection: Annotated[Connection, Depends(get_connection)],
    operation_id: Annotated[int, Path(ge=1, description="Идентификатор операции")],
):
    row = await repositories.get_write_off(connection, operation_id)

    if row is None:
        raise APIException(status_code=404, code="OPERATION_NOT_FOUND", message="Операция не найдена")

    return WriteOffRead.model_validate(dict(row))


@router.post(
    "/write_offs",
    response_model=OperationCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions("operations.write_off.create"))],
    summary="Создать прочее списание",
    responses={404: WRITE_OFF_404},
)
async def create_write_off(
    connection: Annotated[Connection, Depends(get_connection)],
    user: Annotated[UserModel, Depends(get_current_user)],
    payload: Annotated[WriteOffCreate, Body()],
):
    if not payload.items:
        raise APIException(status_code=422, code="EMPTY_ITEMS", message="Список позиций не может быть пустым")

    if not await warehouse_exists(connection, payload.warehouse_id):
        raise APIException(status_code=404, code="WAREHOUSE_NOT_FOUND", message="Склад не найден")

    for it in payload.items:
        if not await material_exists(connection, it.material_id):
            raise APIException(status_code=404, code="MATERIAL_NOT_FOUND", message="Материал не найден")

    op_id = await repositories.create_write_off(connection, user.id, payload)
    return OperationCreateResponse(id=op_id)


@router.patch(
    "/write_offs/{operation_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("operations.write_off.update"))],
    summary="Изменить прочее списание",
    responses={404: WRITE_OFF_404},
)
async def update_write_off(
    connection: Annotated[Connection, Depends(get_connection)],
    operation_id: Annotated[int, Path(ge=1, description="Идентификатор операции")],
    payload: Annotated[WriteOffUpdate, Body()],
):
    row = await repositories.get_write_off(connection, operation_id)

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

    await repositories.update_write_off(connection, operation_id, payload)
