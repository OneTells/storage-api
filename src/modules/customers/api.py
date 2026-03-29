from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Depends, Query

from core.methods import get_connection, require_permissions
from modules.customers.customer.api import router as customer_router
from modules.customers.schemes import CustomersReadResponse

router = APIRouter(prefix="/customers", tags=["Управление клиентами"])
router.include_router(customer_router)


@router.get(
    "/",
    response_model=CustomersReadResponse,
    dependencies=[Depends(require_permissions('customers.read'))],
    summary="Получить список клиентов",
    responses={
        200: {"description": "Список клиентов успешно получен"},
    }
)
async def get_customers(
    connection: Annotated[Connection, Depends(get_connection)],
    page: Annotated[int, Query(ge=1, description="Номер страницы")],
    limit: Annotated[int, Query(ge=1, le=1000, description="Количество элементов на странице")] = 100,
    is_active: Annotated[bool | None, Query(description="Фильтр по активности клиента")] = None
):
    raise NotImplementedError
