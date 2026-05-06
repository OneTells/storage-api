from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Depends, Query

from core.methods import get_connection, require_permissions
from core.models import UnitCategoryEnum
from core.schemes import Pagination
from modules.units import repositories
from modules.units.schemes import UnitRead, UnitsReadResponse

router = APIRouter(prefix="/units", tags=["Управление единицами измерения"])


@router.get(
    "/",
    response_model=UnitsReadResponse,
    dependencies=[Depends(require_permissions('units.read'))],
    summary="Получить список единиц измерения"
)
async def get_units(
    connection: Annotated[Connection, Depends(get_connection)],
    page: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    limit: Annotated[int, Query(ge=1, le=1000, description="Количество элементов на странице")] = 100,
    category: Annotated[UnitCategoryEnum | None, Query(description="Фильтр по категории единиц")] = None,
    is_base: Annotated[bool | None, Query(description="Фильтр по признаку базовой единицы")] = None
):
    units = await repositories.fetch_units(connection, page, limit, category, is_base)
    total = await repositories.count_units(connection, category, is_base)

    return UnitsReadResponse(
        units=[UnitRead(**x) for x in units],
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            pages=(total + limit - 1) // limit,
            has_next=page * limit < total,
            has_prev=page > 1
        )
    )
