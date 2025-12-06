from typing import Annotated

from fastapi import APIRouter, Query

from core.utils.openapi import INTERNAL_ERROR_RESPONSE
from modules.v1.catalog.schemes import CatalogRead

router = APIRouter(prefix="/catalog", tags=["Каталог объектов по категориям"])


@router.get(
    '/',
    response_model=list[CatalogRead],
    summary="Получить объекты, категории и их связи",
    responses={
        200: {"description": "Объекты, категории и их связи успешно получены"},
        500: INTERNAL_ERROR_RESPONSE,
    }
)
async def get_catalog(
    category_id: Annotated[int | None, Query(ge=1, description="Идентификатор корневой категории")],
    is_active_objects: Annotated[bool | None, Query(description="Активность объектов")]
):
    ...
