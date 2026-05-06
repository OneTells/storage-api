from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Depends, Query

from core.methods import get_connection, require_permissions
from core.models import ResourceType
from core.schemes import Pagination
from modules.resources import repositories
from modules.resources.resource.api import router as resource_router
from modules.resources.schemes import resource_read_adapter, ResourcesReadResponse

router = APIRouter(prefix="/resources", tags=["Управление ресурсами"])
router.include_router(resource_router)


@router.get(
    "/",
    response_model=ResourcesReadResponse,
    dependencies=[Depends(require_permissions('resources.read'))],
    summary="Получить список ресурсов"
)
async def get_resources(
    connection: Annotated[Connection, Depends(get_connection)],
    page: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    limit: Annotated[int, Query(ge=1, le=1000, description="Количество элементов на странице")] = 100,
    resource_type: Annotated[ResourceType | None, Query(description="Фильтр по типу ресурса")] = None
):
    resources = await repositories.fetch_resources(connection, page, limit, resource_type)
    total = await repositories.count_resources(connection, resource_type)

    return ResourcesReadResponse(
        resources=[resource_read_adapter.validate_python(dict(x)) for x in resources],
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            pages=(total + limit - 1) // limit,
            has_next=page * limit < total,
            has_prev=page > 1
        )
    )
