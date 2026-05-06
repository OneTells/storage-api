from asyncpg import Record
from everbase import Connection
from sqlalchemy import func, Select

from core.models import Permission


async def fetch_permissions(connection: Connection, page: int, limit: int) -> list[Record]:
    query = (
        Select(Permission.id, Permission.name, Permission.codename)
        .offset((page - 1) * limit)
        .limit(limit)
    )

    return await connection.fetch(query)


async def count_permissions(connection: Connection) -> int:
    query = Select(func.count(Permission.id))
    return await connection.fetch_val(query)
