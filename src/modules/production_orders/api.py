from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Depends, Query

from core.methods import get_connection, require_permissions
from core.models import ProductionOrderStatus
from core.schemes import Pagination
from modules.production_orders import repositories
from modules.production_orders.production_order.api import router as production_order_router
from modules.production_orders.repositories import production_order_read_from_row
from modules.production_orders.schemes import ProductionOrdersListResponse

router = APIRouter(prefix="/production-orders", tags=["Производственные заказы"])
router.include_router(production_order_router)


@router.get(
    "/",
    response_model=ProductionOrdersListResponse,
    dependencies=[Depends(require_permissions("production_orders.read"))],
    summary="Список производственных заказов",
)
async def list_production_orders(
    connection: Annotated[Connection, Depends(get_connection)],
    page: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    limit: Annotated[int, Query(ge=1, le=500, description="Размер страницы")] = 200,
    status: Annotated[
        ProductionOrderStatus | None,
        Query(description="Фильтр по статусу заказа"),
    ] = None,
):
    rows = await repositories.fetch_production_orders(connection, page, limit, status)
    total = await repositories.count_production_orders(connection, status)

    return ProductionOrdersListResponse(
        production_orders=[production_order_read_from_row(r) for r in rows],
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            pages=(total + limit - 1) // limit if total else 0,
            has_next=page * limit < total if total else False,
            has_prev=page > 1 if total else False,
        ),
    )
