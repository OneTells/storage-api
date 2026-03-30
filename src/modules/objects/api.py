from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Depends, Query

from core.methods import get_connection, require_permissions
from modules.objects.object.api import router as object_router
from modules.objects.schemes import ObjectsReadResponse

router = APIRouter(prefix="/objects", tags=["Управление объектами"])
router.include_router(object_router)


@router.get(
    "/",
    response_model=ObjectsReadResponse,
    dependencies=[Depends(require_permissions('objects.read'))],
    summary="Получить список объектов",
)
async def get_objects(
    connection: Annotated[Connection, Depends(get_connection)],
    page: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    limit: Annotated[int, Query(ge=1, le=1000, description="Количество элементов на странице")] = 100,
    is_active: Annotated[bool | None, Query(description="Фильтр по активности объекта")] = None
):
    raise NotImplementedError
