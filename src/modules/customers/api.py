from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Depends, Query

from core.methods import get_connection, require_permissions
from core.schemes import Pagination
from modules.customers import repositories
from modules.customers.customer.api import router as customer_router
from modules.customers.schemes import customer_read_adapter, CustomersReadResponse

router = APIRouter(prefix="/customers", tags=["Управление клиентами"])
router.include_router(customer_router)


@router.get(
    "/",
    response_model=CustomersReadResponse,
    dependencies=[Depends(require_permissions('customers.read'))],
    summary="Получить список клиентов",
)
async def get_customers(
    connection: Annotated[Connection, Depends(get_connection)],
    page: Annotated[int, Query(ge=1, description="Номер страницы")],
    limit: Annotated[int, Query(ge=1, le=1000, description="Количество элементов на странице")] = 100,
    is_active: Annotated[bool | None, Query(description="Фильтр по активности клиента")] = None
):
    customers_data = await repositories.fetch_customers(connection, page, limit, is_active)
    total = await repositories.count_customers(connection, is_active)

    return CustomersReadResponse(
        customers=[customer_read_adapter.validate_python(dict(x)) for x in customers_data],
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            pages=(total + limit - 1) // limit,
            has_next=page * limit < total,
            has_prev=page > 1
        )
    )
