from typing import Annotated


from fastapi import APIRouter, Query
from sqlalchemy import Select

from core.models import Supplier
from core.objects import database
from core.utils.openapi import INTERNAL_ERROR_RESPONSE
from modules.v1.suppliers.schemas import SupplierRead
from modules.v1.suppliers.supplier.api import router as supplier_router

router = APIRouter(prefix="/suppliers", tags=["Управление поставщиками"])
router.include_router(supplier_router)


@router.get(
    '/',
    response_model=list[SupplierRead],
    summary="Получить список поставщиков",
    responses={
        200: {"description": "Список поставщиков успешно получен"},
    },
)
async def get_suppliers(
    page: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    limit: Annotated[int, Query(ge=1, le=1000, description="Количество элементов на странице")] = 100,
    is_active: Annotated[bool | None, Query(description="Фильтр по активности поставщика")] = None
):
    query = (
        Select(
            Supplier.id,
            Supplier.name,
            Supplier.is_active,
            Supplier.created_at
        )
        .order_by(Supplier.id)
        .offset((page - 1) * limit)
        .limit(limit)
    )

    if is_active is not None:
        query = query.where(Supplier.is_active == is_active)

    async with database.get_connection() as connection:
        response = await query.fetch_all(connection, model=lambda x: dict(x))

    return response
