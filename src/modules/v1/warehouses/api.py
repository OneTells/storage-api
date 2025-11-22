from typing import Annotated

from everbase import Select
from fastapi import APIRouter, Query

from core.models import Warehouse
from core.objects import database
from core.utils.openapi import INTERNAL_ERROR_RESPONSE
from modules.v1.warehouses.schemes import WarehouseRead
from modules.v1.warehouses.warehouse.api import router as warehouse_router

router = APIRouter(prefix="/warehouses", tags=["Управление складом"])
router.include_router(warehouse_router)


@router.get(
    "/",
    response_model=list[WarehouseRead],
    summary="Получить список всех складов",
    responses={
        200: {"description": "Список складов успешно получен"},
        500: INTERNAL_ERROR_RESPONSE,
    },
)
async def get_warehouses(
    page: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    limit: Annotated[int, Query(ge=1, le=1000, description="Количество элементов на странице")] = 100,
    is_active: Annotated[bool | None, Query(description="Фильтр по активности склада")] = None
):
    query = (
        Select(
            Warehouse.id,
            Warehouse.name,
            Warehouse.address,
            Warehouse.is_active,
            Warehouse.created_at
        )
        .order_by(Warehouse.id)
        .offset((page - 1) * limit)
        .limit(limit)
    )

    if is_active is not None:
        query = query.where(Warehouse.is_active == is_active)

    async with database.get_connection() as connection:
        response = await query.fetch_all(connection, model=lambda x: dict(x))

    return response
