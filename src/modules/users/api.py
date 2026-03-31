from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Depends, Query

from core.methods import get_connection, require_permissions
from modules.users.profile.api import router as profile_router
from modules.users.schemes import UsersReadResponse
from modules.users.user.api import router as user_router

router = APIRouter(prefix="/users", tags=["Управление пользователями"])
router.include_router(user_router)
router.include_router(profile_router)


@router.get(
    "/",
    response_model=UsersReadResponse,
    dependencies=[Depends(require_permissions('users.read'))],
    summary="Получить список пользователей",
)
async def get_users(
    connection: Annotated[Connection, Depends(get_connection)],
    page: Annotated[int, Query(ge=1, description="Номер страницы")],
    limit: Annotated[int, Query(ge=1, le=1000, description="Количество элементов на странице")] = 100,
    is_active: Annotated[bool | None, Query(description="Фильтр по активности пользователя")] = None
):
    raise NotImplementedError
