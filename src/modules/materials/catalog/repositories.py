from asyncpg import Record
from everbase import Connection
from sqlalchemy import and_, exists, func, Select

from core.models import Batch, Material, MaterialCategory, MaterialCategoryMaterial, MaterialCategorySubcategory, Unit, Warehouse


async def warehouse_exists(connection: Connection, warehouse_id: int) -> bool:
    query = Select(
        Select(1)
        .select_from(Warehouse)
        .where(Warehouse.id == warehouse_id)
        .exists()
    )

    return await connection.fetch_val(query)


async def fetch_catalog_categories(connection: Connection) -> list[Record]:
    query = (
        Select(
            MaterialCategory.id,
            MaterialCategory.name,
            MaterialCategory.description,
            MaterialCategory.created_at,
        )
        .order_by(MaterialCategory.id)
    )

    return await connection.fetch(query)


async def fetch_catalog_materials(
    connection: Connection,
    is_active_materials: bool | None,
    warehouse_id: int | None,
    is_active_warehouse: bool | None,
) -> list[Record]:
    batch_totals = (
        Select(
            Batch.material_id,
            func.coalesce(func.sum(Batch.remaining), 0).label('remaining_quantity'),
        )
        .select_from(Batch)
    )

    if is_active_warehouse is not None:
        batch_totals = batch_totals.join(Warehouse, Warehouse.id == Batch.warehouse_id)

    if warehouse_id is not None:
        batch_totals = batch_totals.where(Batch.warehouse_id == warehouse_id)

    if is_active_warehouse is not None:
        batch_totals = batch_totals.where(Warehouse.is_active == is_active_warehouse)

    batch_totals_subquery = (
        batch_totals
        .group_by(Batch.material_id)
        .subquery()
    )

    query = (
        Select(
            Material.id,
            Material.sku,
            Material.name,
            Material.description,
            Material.is_active,
            Material.created_at,
            Unit.id.label('unit_id'),
            Unit.name.label('unit_name'),
            Unit.short_name.label('unit_short_name'),
            func.coalesce(batch_totals_subquery.c.remaining_quantity, 0).label('remaining_quantity'),
        )
        .join(Unit, Material.unit_id == Unit.id)
        .outerjoin(batch_totals_subquery, batch_totals_subquery.c.material_id == Material.id)
        .order_by(Material.id)
    )

    if is_active_materials is not None:
        query = query.where(Material.is_active == is_active_materials)

    if warehouse_id is not None or is_active_warehouse is not None:
        batch_conditions = [Batch.material_id == Material.id]

        if warehouse_id is not None:
            batch_conditions.append(Batch.warehouse_id == warehouse_id)

        if is_active_warehouse is not None:
            batch_conditions.append(Warehouse.is_active == is_active_warehouse)

        query = query.where(
            exists(
                Select(1)
                .select_from(Batch)
                .join(Warehouse, Warehouse.id == Batch.warehouse_id)
                .where(and_(*batch_conditions))
            )
        )

    return await connection.fetch(query)


async def fetch_catalog_category_material_links(connection: Connection, material_ids: list[int]) -> list[Record]:
    query = (
        Select(MaterialCategoryMaterial.category_id, MaterialCategoryMaterial.material_id)
        .where(MaterialCategoryMaterial.material_id.in_(material_ids))
    )

    return await connection.fetch(query)


async def fetch_catalog_category_subcategory_links(connection: Connection) -> list[Record]:
    query = Select(MaterialCategorySubcategory.category_id, MaterialCategorySubcategory.subcategory_id)
    return await connection.fetch(query)
