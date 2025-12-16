from everbase import Connection
from sqlalchemy import func, Select

from core.models import Warehouse
from modules.v1.warehouses.schemas import WarehouseRead


async def fetch_warehouses(
    connection: Connection,
    page: int,
    limit: int,
    is_active: bool | None = None
) -> list[WarehouseRead]:
    query = (
        Select(
            Warehouse.id,
            Warehouse.name,
            Warehouse.address,
            Warehouse.is_active,
            Warehouse.created_at
        )
        .order_by(Warehouse.id)
        .offset((page - 1) * limit)
        .limit(limit)
    )

    if is_active is not None:
        query = query.where(Warehouse.is_active == is_active)

    return await connection.fetch(query, model=WarehouseRead)


async def count_warehouses(connection: Connection, is_active: bool | None = None) -> int:
    query = (
        Select(func.count())
    )

    if is_active is not None:
        query = query.where(Warehouse.is_active == is_active)

    return await connection.fetch_val(query)
