from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy import Select

from core.models import Category
from core.objects import database
from core.utils.openapi import INTERNAL_ERROR_RESPONSE
from modules.v1.categories.category.api import router as category_router
from modules.v1.categories.schemas import CategoryRead

router = APIRouter(prefix="/categories", tags=["Управление категориями"])
router.include_router(category_router)


@router.get(
    '/',
    response_model=list[CategoryRead],
    summary="Получить список категорий",
    responses={
        200: {"description": "Список категорий успешно получен"},
    }
)
async def get_categories(
    page: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    limit: Annotated[int, Query(ge=1, le=1000, description="Количество элементов на странице")] = 100
):
    async with database.get_connection() as connection:
        response = await (
            Select(
                Category.id,
                Category.name,
                Category.description,
                Category.created_at
            )
            .order_by(Category.id)
            .offset((page - 1) * limit)
            .limit(limit)
            .fetch_all(connection, model=lambda x: dict(x))
        )

    return response
