from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Depends, Query

from core.methods import get_connection, require_permissions
from modules.roles.role.api import router as role_router
from modules.roles.schemes import RolesReadResponse

router = APIRouter(prefix="/roles", tags=["Управление ролями"])
router.include_router(role_router)


@router.get(
    "/",
    response_model=RolesReadResponse,
    dependencies=[Depends(require_permissions('roles.read'))],
    summary="Получить список ролей",
    responses={
        200: {"description": "Список ролей успешно получен"},
    }
)
async def get_roles(
    connection: Annotated[Connection, Depends(get_connection)],
    page: Annotated[int, Query(ge=1, description="Номер страницы")],
    limit: Annotated[int, Query(ge=1, le=1000, description="Количество элементов на странице")] = 100,
    is_active: Annotated[bool | None, Query(description="Фильтр по активности роли")] = None
):
    raise NotImplementedError
