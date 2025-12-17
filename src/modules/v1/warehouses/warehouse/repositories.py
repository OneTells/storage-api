from everbase import Connection
from sqlalchemy import Select, Update
from sqlalchemy.dialects.postgresql import Insert

from core.models import Warehouse
from modules.v1.warehouses.schemas import WarehouseRead
from modules.v1.warehouses.warehouse.schemas import WarehouseCreate, WarehouseUpdate


async def create_warehouse(connection: Connection, payload: WarehouseCreate) -> int:
    query = (
        Insert(Warehouse)
        .values(**payload.model_dump())
        .returning(Warehouse.id)
    )

    return await connection.fetch_val(query)


async def get_warehouse_by_id(connection: Connection, warehouse_id: int) -> WarehouseRead | None:
    query = (
        Select(
            Warehouse.id,
            Warehouse.name,
            Warehouse.address,
            Warehouse.is_active,
            Warehouse.created_at
        )
        .where(Warehouse.id == warehouse_id)
    )

    return await connection.fetch_row(query, model=WarehouseRead)


async def update_warehouse(connection: Connection, warehouse_id: int, payload: WarehouseUpdate) -> int | None:
    query = (
        Update(Warehouse)
        .values(**payload.model_dump())
        .where(Warehouse.id == warehouse_id)
        .returning(Warehouse.id)
    )

    return await connection.fetch_val(query)
