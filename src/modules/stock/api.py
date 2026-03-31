from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Depends, Query

from core.methods import get_connection, require_permissions
from core.models import ObjectUnitStatus
from modules.stock.schemes import StockReadResponse

router = APIRouter(prefix="/stock", tags=["Остатки на складах"])


@router.get(
    "/",
    response_model=StockReadResponse,
    dependencies=[Depends(require_permissions("stock.read"))],
    summary="Получить агрегированные остатки на складах",
)
async def get_stock(
    connection: Annotated[Connection, Depends(get_connection)],
    page: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    limit: Annotated[int, Query(ge=1, le=1000, description="Количество элементов на странице")] = 100,
    object_id: Annotated[int | None, Query(ge=1, description="Фильтр по объекту")] = None,
    warehouse_id: Annotated[int | None, Query(ge=1, description="Фильтр по складу")] = None,
    status: Annotated[ObjectUnitStatus | None, Query(description="Фильтр по статусу")] = None,
):
    raise NotImplementedError
