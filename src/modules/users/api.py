from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Depends, Query
from orjson import loads

from core.methods import get_connection, require_permissions
from core.schemes import Pagination
from modules.users import repositories
from modules.users.profile.api import router as profile_router
from modules.users.schemes import UserRead, UsersReadResponse
from modules.users.user.api import router as user_router

router = APIRouter(prefix="/users", tags=["Управление пользователями"])
router.include_router(profile_router)
router.include_router(user_router)


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
    users_data = await repositories.fetch_users(connection, page, limit, is_active)
    total = await repositories.count_users(connection, is_active)

    users = []

    for user in users_data:
        user = dict(user)
        user['roles'] = [loads(x) for x in user['roles']]
        users.append(UserRead(**user))

    return UsersReadResponse(
        users=users,
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            pages=(total + limit - 1) // limit,
            has_next=page * limit < total,
            has_prev=page > 1
        )
    )
