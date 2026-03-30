from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Depends, Query

from core.methods import get_connection, require_permissions
from core.schemes import Pagination
from modules.warehouses import repositories
from modules.warehouses.schemes import WarehousesReadResponse
from modules.warehouses.warehouse.api import router as warehouse_router

router = APIRouter(prefix="/warehouses", tags=["Управление складом"])
router.include_router(warehouse_router)


@router.get(
    "/",
    response_model=WarehousesReadResponse,
    dependencies=[Depends(require_permissions('warehouses.read'))],
    summary="Получить список складов",
    responses={
        200: {"description": "Список складов успешно получен"}
    }
)
async def get_warehouses(
    connection: Annotated[Connection, Depends(get_connection)],
    page: Annotated[int, Query(ge=1, description="Номер страницы")],
    limit: Annotated[int, Query(ge=1, le=1000, description="Количество элементов на странице")] = 100,
    is_active: Annotated[bool | None, Query(description="Фильтр по активности склада")] = None
):
    warehouses = await repositories.fetch_warehouses(connection, page, limit, is_active)
    total = await repositories.count_warehouses(connection, is_active)

    return WarehousesReadResponse(
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
