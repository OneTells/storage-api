from asyncpg import Record
from everbase import Connection
from sqlalchemy import func, Select

from core.models import Permission, Role, RolePermission


async def fetch_roles(connection: Connection, page: int, limit: int) -> list[Record]:
    roles_query = (
        Select(
            Role.id,
            Role.name,
            Role.description,
            func.coalesce(
                func.array_agg(
                    func.jsonb_build_object(
                        'id', Permission.id,
                        'name', Permission.name,
                        'codename', Permission.codename
                    )
                ).filter(Permission.id.isnot(None)),
                []
            ).label('permissions')
        )
        .outerjoin(RolePermission, Role.id == RolePermission.role_id)
        .outerjoin(Permission, Permission.id == RolePermission.permission_id)
        .group_by(Role.id, Role.name, Role.description)
        .order_by(Role.name)
        .offset((page - 1) * limit)
        .limit(limit)
    )

    return await connection.fetch(roles_query)


async def count_roles(connection: Connection) -> int:
    query = Select(func.count(Role.id))
    return await connection.fetch_val(query)
