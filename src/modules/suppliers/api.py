from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Depends, Query

from core.methods import get_connection, require_permissions
from modules.suppliers.schemes import SuppliersReadResponse
from modules.suppliers.supplier.api import router as supplier_router

router = APIRouter(prefix="/suppliers", tags=["Управление поставщиками"])
router.include_router(supplier_router)


@router.get(
    '/',
    response_model=SuppliersReadResponse,
    dependencies=[Depends(require_permissions('suppliers.read'))],
    summary="Получить список поставщиков",
    responses={
        200: {"description": "Список поставщиков успешно получен"},
    },
)
async def get_suppliers(
    connection: Annotated[Connection, Depends(get_connection)],
    page: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    limit: Annotated[int, Query(ge=1, le=1000, description="Количество элементов на странице")] = 100,
    is_active: Annotated[bool | None, Query(description="Фильтр по активности поставщика")] = None
):
    raise NotImplementedError
