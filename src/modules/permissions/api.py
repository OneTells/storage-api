from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Depends, Query

from core.methods import get_connection, require_permissions
from core.schemes import Pagination
from modules.permissions import repositories
from modules.permissions.permission.api import router as permission_router
from modules.permissions.schemes import PermissionRead, PermissionsReadResponse

router = APIRouter(prefix="/permissions", tags=["Управление разрешениями"])
router.include_router(permission_router)


@router.get(
    "/",
    response_model=PermissionsReadResponse,
    dependencies=[Depends(require_permissions('permissions.read'))],
    summary="Получить список разрешений",
)
async def get_permissions(
    connection: Annotated[Connection, Depends(get_connection)],
    page: Annotated[int, Query(ge=1, description="Номер страницы")],
    limit: Annotated[int, Query(ge=1, le=1000, description="Количество элементов на странице")] = 100
):
    permissions = await repositories.fetch_permissions(connection, page, limit)
    total = await repositories.count_permissions(connection)

    return PermissionsReadResponse(
        permissions=[PermissionRead(**x) for x in permissions],
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            pages=(total + limit - 1) // limit,
            has_next=page * limit < total,
            has_prev=page > 1
        )
    )
