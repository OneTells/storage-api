from typing import Annotated
from uuid import UUID

from everbase import Connection
from fastapi import APIRouter, Depends, Path, Query

from core.methods import get_connection, require_permissions
from modules.object_units.object_unit.responses import OBJECT_UNIT_NOT_FOUND
from modules.object_units.object_unit.schemes import ObjectUnitRead, OperationsReadResponse

router = APIRouter()


@router.get(
    '/{object_unit_id}',
    response_model=ObjectUnitRead,
    dependencies=[Depends(require_permissions('object_unit.read'))],
    summary="Получить единицу объекта",
    responses={
        404: OBJECT_UNIT_NOT_FOUND
    }
)
async def get_object_unit(
    connection: Annotated[Connection, Depends(get_connection)],
    object_unit_id: Annotated[UUID, Path(ge=1, description="Идентификатор единицы объекта")],
):
    raise NotImplementedError


@router.get(
    '/{object_unit_id}/operations',
    response_model=OperationsReadResponse,
    dependencies=[Depends(require_permissions('object_unit.operations.read'))],
    summary="Получить операции для единицы объекта",
    responses={
        404: OBJECT_UNIT_NOT_FOUND
    }
)
async def get_operations(
    connection: Annotated[Connection, Depends(get_connection)],
    object_unit_id: Annotated[UUID, Path(ge=1, description="Идентификатор единицы объекта")],
    page: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    limit: Annotated[int, Query(ge=1, le=1000, description="Количество элементов на странице")] = 100,
):
    raise NotImplementedError
