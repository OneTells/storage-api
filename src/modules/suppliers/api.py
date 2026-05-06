from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Depends, Query

from core.methods import get_connection, require_permissions
from core.schemes import Pagination
from modules.suppliers import repositories
from modules.suppliers.schemes import supplier_read_adapter, SuppliersReadResponse
from modules.suppliers.supplier.api import router as supplier_router

router = APIRouter(prefix="/suppliers", tags=["Управление поставщиками"])
router.include_router(supplier_router)


@router.get(
    '/',
    response_model=SuppliersReadResponse,
    dependencies=[Depends(require_permissions('suppliers.read'))],
    summary="Получить список поставщиков",
)
async def get_suppliers(
    connection: Annotated[Connection, Depends(get_connection)],
    page: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    limit: Annotated[int, Query(ge=1, le=1000, description="Количество элементов на странице")] = 100,
    is_active: Annotated[bool | None, Query(description="Фильтр по активности поставщика")] = None
):
    suppliers_data = await repositories.fetch_suppliers(connection, page, limit, is_active)
    total = await repositories.count_suppliers(connection, is_active)

    return SuppliersReadResponse(
        suppliers=[supplier_read_adapter.validate_python(dict(x)) for x in suppliers_data],
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            pages=(total + limit - 1) // limit,
            has_next=page * limit < total,
            has_prev=page > 1
        )
    )
