from asyncpg import Record
from everbase import Connection
from sqlalchemy import Select, Update
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import aliased

from core.models import Permission, Role, RolePermission, User, UserSession, UserRole


async def get_user_profile_data(connection: Connection, user_id: int, sessions_limit: int = 10) -> Record | None:
    # Получаем основную информацию о пользователе
    user_query = (
        Select(User.id, User.name, User.username, User.is_active, User.created_at)
        .where(User.id == user_id)
    )
    
    user_data = await connection.fetch_row(user_query)
    
    if user_data is None:
        return None
    
    # Получаем роли пользователя
    roles_query = (
        Select(Role.id, Role.name, Role.description)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user_id)
        .order_by(Role.name)
    )
    
    roles = await connection.fetch(roles_query)
    
    # Получаем разрешения пользователя через роли
    permissions_query = (
        Select(Permission.id, Permission.name, Permission.codename)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(Role, Role.id == RolePermission.role_id)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user_id)
        .distinct()
        .order_by(Permission.name)
    )
    
    permissions = await connection.fetch(permissions_query)
    
    # Получаем сессии пользователя с ограничением
    sessions_query = (
        Select(UserSession.id, UserSession.is_active, UserSession.created_at, UserSession.deactivated_at)
        .where(UserSession.user_id == user_id)
        .order_by(UserSession.created_at.desc())
        .limit(sessions_limit)
    )
    
    sessions = await connection.fetch(sessions_query)
    
    # Комбинируем все данные в одну запись
    return {
        **user_data,
        'roles': roles,
        'permissions': permissions,
        'sessions': sessions
    }


async def exist_user_by_username(connection: Connection, username: str, exclude_user_id: int | None = None) -> bool:
    query = (
        Select(
            Select(1)
            .select_from(User)
            .where(User.username == username)
        )
    )

    if exclude_user_id is not None:
        query = query.where(User.id != exclude_user_id)

    query = Select(query.exists())

    return await connection.fetch_val(query)


async def update_user(
    connection: Connection, 
    user_id: int, 
    name: str, 
    username: str, 
    password_hash: str, 
    is_active: bool
) -> None:
    query = (
        Update(User)
        .values(name=name, username=username, password_hash=password_hash, is_active=is_active)
        .where(User.id == user_id)
    )

    await connection.execute(query)
