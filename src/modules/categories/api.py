from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Depends, Query

from core.methods import get_connection, require_permissions
from modules.categories.category.api import router as category_router
from modules.categories.schemes import CategoriesReadResponse

router = APIRouter(prefix="/categories", tags=["Управление категориями"])
router.include_router(category_router)


@router.get(
    "/",
    response_model=CategoriesReadResponse,
    dependencies=[Depends(require_permissions("categories.read"))],
    summary="Получить список категорий",
)
async def get_categories(
    connection: Annotated[Connection, Depends(get_connection)],
    page: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    limit: Annotated[int, Query(ge=1, le=1000, description="Количество элементов на странице")] = 100
):
    raise NotImplementedError
