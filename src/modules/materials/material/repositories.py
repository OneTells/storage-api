from asyncpg import Record
from everbase import Connection
from sqlalchemy import Select, Update, func
from sqlalchemy.dialects.postgresql import Insert

from core.models import Batch, Material, Unit, Warehouse
from modules.materials.material.schemes import MaterialCreate, MaterialUpdate


async def get_material_by_id(connection: Connection, material_id: int) -> Record | None:
    query = (
        Select(
            Material.id,
            Material.sku,
            Material.name,
            Material.description,
            Material.unit_id,
            Material.is_active,
            Material.created_at,
        )
        .where(Material.id == material_id)
    )
    return await connection.fetch_row(query)


async def fetch_material_warehouse_stocks(connection: Connection, material_id: int) -> list[Record]:
    query = (
        Select(
            Warehouse.id.label("warehouse_id"),
            Warehouse.name.label("warehouse_name"),
            Warehouse.is_active.label("warehouse_is_active"),
            func.coalesce(func.sum(Batch.remaining), 0).label("remaining_quantity"),
        )
        .select_from(Batch)
        .join(Warehouse, Warehouse.id == Batch.warehouse_id)
        .where(Batch.material_id == material_id)
        .group_by(Warehouse.id, Warehouse.name, Warehouse.is_active)
        .order_by(Warehouse.id)
    )

    return await connection.fetch(query)


async def exists_material_by_sku(connection: Connection, sku: str, *, exclude_material_id: int | None = None) -> bool:
    inner = Select(1).select_from(Material).where(Material.sku == sku)

    if exclude_material_id is not None:
        inner = inner.where(Material.id != exclude_material_id)

    query = Select(inner.exists())
    return await connection.fetch_val(query)


async def exists_unit(connection: Connection, unit_id: int) -> bool:
    query = Select(
        Select(1)
        .select_from(Unit)
        .where(Unit.id == unit_id)
        .exists()
    )

    return await connection.fetch_val(query)


async def create_material(connection: Connection, payload: MaterialCreate) -> int:
    query = (
        Insert(Material)
        .values(
            sku=payload.sku,
            name=payload.name,
            description=payload.description,
            unit_id=payload.unit_id,
            is_active=payload.is_active,
        )
        .returning(Material.id)
    )

    return await connection.fetch_val(query)


async def update_material(connection: Connection, material_id: int, payload: MaterialUpdate) -> None:
    query = (
        Update(Material)
        .values(
            sku=payload.sku,
            name=payload.name,
            description=payload.description,
            unit_id=payload.unit_id,
            is_active=payload.is_active,
        )
        .where(Material.id == material_id)
    )

    await connection.execute(query)
