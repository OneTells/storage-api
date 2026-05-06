from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Depends, Query
from orjson import loads

from core.methods import get_connection, require_permissions
from core.schemes import Pagination
from modules.roles import repositories
from modules.roles.role.api import router as role_router
from modules.roles.schemes import RoleRead, RolesReadResponse

router = APIRouter(prefix="/roles", tags=["Управление ролями"])
router.include_router(role_router)


@router.get(
    "/",
    response_model=RolesReadResponse,
    dependencies=[Depends(require_permissions('roles.read'))],
    summary="Получить список ролей",
)
async def get_roles(
    connection: Annotated[Connection, Depends(get_connection)],
    page: Annotated[int, Query(ge=1, description="Номер страницы")],
    limit: Annotated[int, Query(ge=1, le=1000, description="Количество элементов на странице")] = 100
):
    roles_data = await repositories.fetch_roles(connection, page, limit)
    total = await repositories.count_roles(connection)

    roles = []

    for role in roles_data:
        role = dict(role)
        role['permissions'] = [loads(x) for x in role['permissions']]
        roles.append(RoleRead(**role))

    return RolesReadResponse(
        roles=roles,
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            pages=(total + limit - 1) // limit,
            has_next=page * limit < total,
            has_prev=page > 1
        )
    )
