from asyncpg import Record
from everbase import Connection
from sqlalchemy import func, Select

from core.models import Role, User, UserRole, UserSession


async def fetch_users(connection: Connection, page: int, limit: int, is_active: bool | None = None) -> list[Record]:
    query = (
        Select(
            User.id,
            User.name,
            User.username,
            User.is_active,
            User.created_at,
            func.coalesce(
                func.array_agg(
                    func.jsonb_build_object(
                        'id', Role.id,
                        'name', Role.name,
                        'description', Role.description
                    )
                ).filter(Role.id.isnot(None)),
                []
            ).label('roles'),
            func.coalesce(
                func.count(func.nullif(UserSession.is_active, False)),
                0
            ).label('active_sessions')
        )
        .outerjoin(UserRole, User.id == UserRole.user_id)
        .outerjoin(Role, Role.id == UserRole.role_id)
        .outerjoin(UserSession, (User.id == UserSession.user_id) & (UserSession.is_active == True))
        .group_by(User.id, User.name, User.username, User.is_active, User.created_at)
        .order_by(User.username)
        .offset((page - 1) * limit)
        .limit(limit)
    )

    if is_active is not None:
        query = query.where(User.is_active == is_active)

    return await connection.fetch(query)


async def count_users(connection: Connection, is_active: bool | None = None) -> int:
    query = Select(func.count(User.id))

    if is_active is not None:
        query = query.where(User.is_active == is_active)

    return await connection.fetch_val(query)
