from typing import Annotated

from fastapi import APIRouter, Query

from core.methods.response import JSONResponse
from core.objects import database
from core.schemas import Pagination
from modules.v1.warehouses import repositories
from modules.v1.warehouses.schemas import WarehousesReadResponse
from modules.v1.warehouses.warehouse.api import router as warehouse_router

router = APIRouter(prefix="/warehouses", tags=["Управление складом"])
router.include_router(warehouse_router)


@router.get(
    "/",
    response_model=WarehousesReadResponse,
    summary="Получить список всех складов",
    responses={
        200: {"description": "Список складов успешно получен"},
    },
)
async def get_warehouses(
    page: Annotated[int, Query(ge=1, description="Номер страницы")],
    limit: Annotated[int, Query(ge=1, le=1000, description="Количество элементов на странице")] = 100,
    is_active: Annotated[bool | None, Query(description="Фильтр по активности склада")] = None
):
    async with database.acquire() as connection:
        warehouses = await repositories.fetch_warehouses(connection, page, limit, is_active)
        total = await repositories.count_warehouses(connection, is_active)

    return JSONResponse(
        content=WarehousesReadResponse(
            warehouses=warehouses,
            pagination=Pagination(
                page=page,
                limit=limit,
                total=total,
                pages=(total + limit - 1) // limit,
                has_next=page * limit < total,
                has_prev=page > 1
            )
        )
    )
