from asyncpg import Record
from everbase import Connection
from sqlalchemy import func, Select

from core.models import Role


async def fetch_roles(connection: Connection, page: int, limit: int) -> list[Record]:
    query = (
        Select(Role.id, Role.name)
        .offset((page - 1) * limit)
        .limit(limit)
    )

    return await connection.fetch(query)


async def count_roles(connection: Connection) -> int:
    query = Select(func.count(Role.id))
    return await connection.fetch_val(query)
