from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Depends, Query

from core.methods import get_connection, require_permissions
from core.models import ObjectUnitStatus
from modules.object_units.object_unit.api import router as object_unit_router
from modules.object_units.schemes import ObjectUnitsReadResponse

router = APIRouter(prefix="/object-units", tags=["Управление юнитами объектов"])
router.include_router(object_unit_router)


@router.get(
    '/',
    response_model=ObjectUnitsReadResponse,
    dependencies=[Depends(require_permissions('object_units.read'))],
    summary="Получить список единиц объекта",
)
async def get_object_units(
    connection: Annotated[Connection, Depends(get_connection)],
    page: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    limit: Annotated[int, Query(ge=1, le=1000, description="Количество элементов на странице")] = 100,
    object_id: Annotated[int | None, Query(ge=1, description="Фильтр по объекту")] = None,
    warehouse_id: Annotated[int | None, Query(ge=1, description="Фильтр по складу")] = None,
    status: Annotated[ObjectUnitStatus | None, Query(description="Фильтр по статусу")] = None,
):
    raise NotImplementedError
