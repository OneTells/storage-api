from asyncpg import Record
from everbase import Connection
from sqlalchemy import func, Select

from core.models import Employee


async def fetch_employees(connection: Connection, page: int, limit: int) -> list[Record]:
    query = (
        Select(
            Employee.id,
            Employee.full_name,
            Employee.position,
            Employee.default_hourly_rate,
            Employee.created_at
        )
        .order_by(Employee.id)
        .offset((page - 1) * limit)
        .limit(limit)
    )

    return await connection.fetch(query)


async def count_employees(connection: Connection) -> int:
    query = Select(func.count(Employee.id))
    return await connection.fetch_val(query)
