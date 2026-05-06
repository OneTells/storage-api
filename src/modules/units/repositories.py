from asyncpg import Record
from everbase import Connection
from sqlalchemy import func, Select

from core.models import Unit, UnitCategoryEnum


async def fetch_units(
    connection: Connection,
    page: int,
    limit: int,
    category: UnitCategoryEnum | None = None,
    is_base: bool | None = None
) -> list[Record]:
    query = (
        Select(
            Unit.id,
            Unit.category,
            Unit.name,
            Unit.short_name,
            Unit.conversion_factor,
            Unit.is_base,
            Unit.created_at
        )
        .order_by(Unit.id)
        .offset((page - 1) * limit)
        .limit(limit)
    )

    if category is not None:
        query = query.where(Unit.category == category)

    if is_base is not None:
        query = query.where(Unit.is_base == is_base)

    return await connection.fetch(query)


async def count_units(
    connection: Connection,
    category: UnitCategoryEnum | None = None,
    is_base: bool | None = None
) -> int:
    query = Select(func.count(Unit.id))

    if category is not None:
        query = query.where(Unit.category == category)

    if is_base is not None:
        query = query.where(Unit.is_base == is_base)

    return await connection.fetch_val(query)
