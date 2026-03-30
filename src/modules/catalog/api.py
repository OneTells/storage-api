from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Depends, Query

from core.methods import get_connection, require_permissions
from core.schemes import ErrorCode, ErrorResponse
from modules.catalog.schemes import CatalogReadResponse

router = APIRouter(prefix="/catalog", tags=["Каталог объектов по категориям"])


@router.get(
    '/',
    response_model=CatalogReadResponse,
    dependencies=[Depends(require_permissions('catalog.read'))],
    summary="Получить объекты, категории и их связи",
    responses={
        200: {
            "description": "Объекты, категории и их связи успешно получены"
        },
        404: {
            "description": "Категория не найдена",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "code": ErrorCode.CATEGORY_NOT_FOUND,
                        "message": "Категория не найдена",
                        "params": {}
                    }
                }
            }
        }
    }
)
async def get_catalog(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int | None, Query(ge=1, description="Идентификатор корневой категории")],
    is_active_objects: Annotated[bool | None, Query(description="Фильтр по активности объектов")] = None
):
    raise NotImplementedError
