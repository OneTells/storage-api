from asyncpg import Record
from everbase import Connection
from sqlalchemy import func, Select, Update

from core.models import Permission, Role, RolePermission, User, UserRole, UserSession


async def get_user_profile_data(connection: Connection, user_id: int, sessions_limit: int) -> Record | None:
    sessions_subquery = (
        Select(
            UserSession.id,
            UserSession.user_id,
            UserSession.is_active,
            UserSession.created_at,
            UserSession.deactivated_at
        )
        .where(UserSession.user_id == user_id)
        .order_by(UserSession.created_at.desc())
        .limit(sessions_limit)
        .subquery()
    )

    query = (
        Select(
            User.id,
            User.name,
            User.username,
            User.is_active,
            User.created_at,
            func.coalesce(
                func.array_agg(
                    func.distinct(
                        func.jsonb_build_object(
                            'id', Role.id,
                            'name', Role.name,
                            'description', Role.description
                        )
                    )
                ).filter(Role.id.isnot(None)),
                []
            ).label('roles'),
            func.coalesce(
                func.array_agg(
                    func.distinct(
                        func.jsonb_build_object(
                            'id', Permission.id,
                            'name', Permission.name,
                            'codename', Permission.codename
                        )
                    )
                ).filter(Permission.id.isnot(None)),
                []
            ).label('permissions'),
            func.coalesce(
                func.array_agg(
                    func.distinct(
                        func.jsonb_build_object(
                            'id', sessions_subquery.c.id,
                            'is_active', sessions_subquery.c.is_active,
                            'created_at', sessions_subquery.c.created_at,
                            'deactivated_at', sessions_subquery.c.deactivated_at
                        )
                    )
                ).filter(sessions_subquery.c.id.isnot(None)),
                []
            ).label('sessions')
        )
        .outerjoin(UserRole, User.id == UserRole.user_id)
        .outerjoin(Role, Role.id == UserRole.role_id)
        .outerjoin(RolePermission, Role.id == RolePermission.role_id)
        .outerjoin(Permission, Permission.id == RolePermission.permission_id)
        .outerjoin(sessions_subquery, User.id == sessions_subquery.c.user_id)
        .where(User.id == user_id)
        .group_by(User.id, User.name, User.username, User.is_active, User.created_at)
    )

    return await connection.fetch_row(query)


async def exist_user_by_username(connection: Connection, username: str) -> bool:
    query = (
        Select(
            Select(1)
            .select_from(User)
            .where(User.username == username)
            .exists()
        )
    )

    return await connection.fetch_val(query)


async def get_user_username(connection: Connection, user_id: int) -> str | None:
    query = (
        Select(User.username)
        .where(User.id == user_id)
    )

    return await connection.fetch_val(query)


async def update_user(
    connection: Connection,
    user_id: int,
    name: str,
    username: str
) -> None:
    query = (
        Update(User)
        .values(name=name, username=username)
        .where(User.id == user_id)
    )

    await connection.execute(query)


async def update_user_password(
    connection: Connection,
    user_id: int,
    password_hash: str
) -> None:
    query = (
        Update(User)
        .values(password_hash=password_hash)
        .where(User.id == user_id)
    )

    await connection.execute(query)
