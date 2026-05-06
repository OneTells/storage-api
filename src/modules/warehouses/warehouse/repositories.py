from asyncpg import Record
from everbase import Connection
from sqlalchemy import Select, Update
from sqlalchemy.dialects.postgresql import Insert

from core.models import Warehouse
from modules.warehouses.schemes import WarehouseRead
from modules.warehouses.warehouse.schemes import WarehouseCreate, WarehouseUpdate


async def create_warehouse(connection: Connection, payload: WarehouseCreate) -> int:
    query = (
        Insert(Warehouse)
        .values(**payload.model_dump())
        .returning(Warehouse.id)
    )

    return await connection.fetch_val(query)


async def get_warehouse_by_id(connection: Connection, warehouse_id: int) -> Record | None:
    query = (
        Select(
            Warehouse.id,
            Warehouse.name,
            Warehouse.comment,
            Warehouse.is_active,
            Warehouse.created_at
        )
        .where(Warehouse.id == warehouse_id)
    )

    return await connection.fetch_row(query)


async def exist_warehouse_by_name(connection: Connection, name: str) -> bool:
    query = (
        Select(
            Select(1)
            .select_from(Warehouse)
            .where(Warehouse.name == name)
            .exists()
        )
    )

    return await connection.fetch_val(query)


async def update_warehouse(connection: Connection, warehouse_id: int, payload: WarehouseUpdate) -> None:
    query = (
        Update(Warehouse)
        .values(**payload.model_dump())
        .where(Warehouse.id == warehouse_id)
    )

    await connection.execute(query)
