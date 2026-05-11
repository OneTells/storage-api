from decimal import Decimal
from typing import NamedTuple

from asyncpg import Record
from everbase import Connection
from sqlalchemy import Delete, func, Select, Update
from sqlalchemy.dialects.postgresql import Insert
from sqlalchemy.orm import aliased

from core.models import (
    Batch,
    Material,
    Product,
    ProductCategoryProduct,
    ProductMaterial,
    ProductResource,
    Resource,
    Unit,
    Warehouse,
)
from modules.products.product.schemes import ProductCreate, ProductUpdate


def _product_materials_subquery():
    return (
        Select(
            func.coalesce(
                func.array_agg(
                    func.jsonb_build_object(
                        "id", ProductMaterial.material_id,
                        "name", Material.name,
                        "quantity", ProductMaterial.quantity,
                        "unit",
                        func.jsonb_build_object(
                            "id", Unit.id,
                            "name", Unit.name,
                            "short_name", Unit.short_name,
                        ),
                    )
                ),
                [],
            )
        )
        .select_from(ProductMaterial)
        .join(Material, Material.id == ProductMaterial.material_id)
        .join(Unit, Unit.id == Material.unit_id)
        .where(ProductMaterial.product_id == Product.id)
        .scalar_subquery()
    )


def _product_resources_subquery():
    return (
        Select(
            func.coalesce(
                func.array_agg(
                    func.jsonb_build_object(
                        "id", ProductResource.resource_id,
                        "name", Resource.name,
                        "quantity", ProductResource.quantity,
                        "unit",
                        func.jsonb_build_object(
                            "id", Unit.id,
                            "name", Unit.name,
                            "short_name", Unit.short_name,
                        ),
                    )
                ),
                [],
            )
        )
        .select_from(ProductResource)
        .join(Resource, Resource.id == ProductResource.resource_id)
        .join(Unit, Unit.id == Resource.unit_id)
        .where(ProductResource.product_id == Product.id)
        .scalar_subquery()
    )


async def get_product_by_id(connection: Connection, product_id: int) -> Record | None:
    materials_subquery = _product_materials_subquery()
    resources_subquery = _product_resources_subquery()
    output_material = aliased(Material)
    output_unit = aliased(Unit)

    query = (
        Select(
            Product.id,
            Product.name,
            Product.description,
            Product.is_active,
            Product.output_material_id,
            output_material.name.label("output_material_name"),
            output_unit.id.label("output_material_unit_id"),
            output_unit.name.label("output_material_unit_name"),
            output_unit.short_name.label("output_material_unit_short_name"),
            Product.output_quantity,
            materials_subquery.label("materials"),
            resources_subquery.label("resources"),
            Product.created_at,
        )
        .select_from(Product)
        .join(output_material, output_material.id == Product.output_material_id)
        .join(output_unit, output_unit.id == output_material.unit_id)
        .where(Product.id == product_id)
    )

    return await connection.fetch_row(query)


async def create_product(connection: Connection, payload: ProductCreate) -> int:
    query = (
        Insert(Product)
        .values(
            name=payload.name,
            description=payload.description,
            is_active=payload.is_active,
            output_material_id=payload.output_material.output_material_id,
            output_quantity=payload.output_material.output_quantity,
        )
        .returning(Product.id)
    )
    return await connection.fetch_val(query)


async def update_product(connection: Connection, product_id: int, payload: ProductUpdate) -> None:
    query = (
        Update(Product)
        .values(
            name=payload.name,
            description=payload.description,
            is_active=payload.is_active,
            output_material_id=payload.output_material.output_material_id,
            output_quantity=payload.output_material.output_quantity,
        )
        .where(Product.id == product_id)
    )
    await connection.execute(query)


async def replace_product_materials(connection: Connection, product_id: int, materials: list[dict]) -> None:
    await connection.execute(
        Delete(ProductMaterial)
        .where(ProductMaterial.product_id == product_id)
    )

    if not materials:
        return

    await connection.execute(
        Insert(ProductMaterial).values(
            [
                {
                    "product_id": product_id,
                    "material_id": material["material_id"],
                    "quantity": material["quantity"]
                }
                for material in materials
            ]
        )
    )


async def replace_product_resources(connection: Connection, product_id: int, resources: list[dict]) -> None:
    await connection.execute(
        Delete(ProductResource).where(ProductResource.product_id == product_id)
    )

    if not resources:
        return

    await connection.execute(
        Insert(ProductResource).values(
            [
                {
                    "product_id": product_id,
                    "resource_id": resource["resource_id"],
                    "quantity": resource["quantity"]
                }
                for resource in resources
            ]
        )
    )


def _products_select_extended_query():
    materials_subquery = _product_materials_subquery()
    resources_subquery = _product_resources_subquery()
    output_material = aliased(Material)
    output_unit = aliased(Unit)
    return (
        Select(
            Product.id,
            Product.name,
            Product.description,
            Product.is_active,
            Product.output_material_id,
            output_material.name.label("output_material_name"),
            output_unit.id.label("output_material_unit_id"),
            output_unit.name.label("output_material_unit_name"),
            output_unit.short_name.label("output_material_unit_short_name"),
            Product.output_quantity,
            materials_subquery.label("materials"),
            resources_subquery.label("resources"),
            Product.created_at,
        )
        .select_from(Product)
        .join(output_material, output_material.id == Product.output_material_id)
        .join(output_unit, output_unit.id == output_material.unit_id)
    )


async def fetch_products_by_category_id(
    connection: Connection,
    category_id: int,
    page: int,
    limit: int,
) -> list[Record]:
    query = (
        _products_select_extended_query()
        .join(ProductCategoryProduct, ProductCategoryProduct.product_id == Product.id)
        .where(ProductCategoryProduct.category_id == category_id)
        .order_by(Product.id)
        .offset((page - 1) * limit)
        .limit(limit)
    )
    return await connection.fetch(query)


async def count_products_by_category_id(connection: Connection, category_id: int) -> int:
    query = (
        Select(func.count(Product.id))
        .join(ProductCategoryProduct, ProductCategoryProduct.product_id == Product.id)
        .where(ProductCategoryProduct.category_id == category_id)
    )
    return await connection.fetch_val(query)


async def fetch_existing_material_ids(connection: Connection, material_ids: list[int]) -> set[int]:
    if not material_ids:
        return set()
    query = Select(Material.id).where(Material.id.in_(material_ids))
    rows = await connection.fetch(query)
    return {row[0] for row in rows}


async def fetch_existing_resource_ids(connection: Connection, resource_ids: list[int]) -> set[int]:
    if not resource_ids:
        return set()
    query = Select(Resource.id).where(Resource.id.in_(resource_ids))
    rows = await connection.fetch(query)
    return {row[0] for row in rows}


async def fetch_existing_product_ids(connection: Connection, product_ids: list[int]) -> set[int]:
    if not product_ids:
        return set()
    query = Select(Product.id).where(Product.id.in_(product_ids))
    rows = await connection.fetch(query)
    return {row[0] for row in rows}


async def fetch_existing_warehouse_ids(connection: Connection, warehouse_ids: list[int]) -> set[int]:
    if not warehouse_ids:
        return set()
    query = Select(Warehouse.id).where(Warehouse.id.in_(warehouse_ids))
    rows = await connection.fetch(query)
    return {row[0] for row in rows}


class ProductBomForShortage(NamedTuple):
    output_quantity: Decimal
    materials: list[tuple[int, Decimal]]


async def fetch_products_bom_for_material_shortage(
    connection: Connection,
    product_ids: list[int],
) -> dict[int, ProductBomForShortage]:
    """Возвращает нормативы (выход и входные материалы) по продуктам."""
    if not product_ids:
        return {}

    query = (
        Select(Product.id, Product.output_quantity, ProductMaterial.material_id, ProductMaterial.quantity)
        .select_from(Product)
        .outerjoin(ProductMaterial, ProductMaterial.product_id == Product.id)
        .where(Product.id.in_(product_ids))
    )
    rows = await connection.fetch(query)

    grouped: dict[int, list[tuple[int, Decimal]]] = {}
    out_qty: dict[int, Decimal] = {}
    for row in rows:
        pid = int(row["id"])
        out_qty[pid] = row["output_quantity"]
        if row["material_id"] is not None:
            grouped.setdefault(pid, []).append((int(row["material_id"]), row["quantity"]))

    return {
        pid: ProductBomForShortage(output_quantity=out_qty[pid], materials=grouped.get(pid, []))
        for pid in out_qty
    }


async def fetch_material_stock_remaining_totals(
    connection: Connection,
    material_ids: list[int],
    warehouse_ids: list[int] | None,
) -> dict[int, Decimal]:
    if not material_ids:
        return {}

    query = (
        Select(Batch.material_id, func.coalesce(func.sum(Batch.remaining), 0))
        .where(Batch.material_id.in_(material_ids))
        .group_by(Batch.material_id)
    )
    if warehouse_ids:
        query = query.where(Batch.warehouse_id.in_(warehouse_ids))

    rows = await connection.fetch(query)
    return {int(row[0]): row[1] for row in rows}


def _max_producible_output_units(
    bom: ProductBomForShortage,
    stock: dict[int, Decimal],
) -> Decimal:
    """Максимум единиц выпуска продукта, ограниченный остатками входных материалов."""
    if not bom.materials:
        return Decimal("Infinity")

    min_units: Decimal | None = None
    out_q = bom.output_quantity
    for material_id, norm_qty in bom.materials:
        if norm_qty <= 0:
            continue
        available = stock.get(material_id, Decimal(0))
        from_material = available * out_q / norm_qty
        min_units = from_material if min_units is None else min(min_units, from_material)

    if min_units is None:
        return Decimal("Infinity")
    return min_units


async def product_material_shortage_lines(
    connection: Connection,
    lines: list[tuple[int, Decimal]],
    warehouse_ids: list[int] | None,
) -> list[tuple[int, Decimal]]:
    """
    Для каждой строки запроса — пара (product_id, нехватка в единицах выпуска).
    Строки с нулевой нехваткой отбрасываются.
    """
    if not lines:
        return []

    product_ids = [p for p, _ in lines]
    boms = await fetch_products_bom_for_material_shortage(connection, product_ids)

    material_ids: set[int] = set()
    for bom in boms.values():
        material_ids.update(mid for mid, _ in bom.materials)

    stock = await fetch_material_stock_remaining_totals(
        connection,
        list(material_ids),
        warehouse_ids,
    )

    out: list[tuple[int, Decimal]] = []
    for product_id, requested in lines:
        bom = boms.get(product_id)
        if bom is None:
            continue

        max_out = _max_producible_output_units(bom, stock)
        if max_out == Decimal("Infinity") or max_out >= requested:
            continue

        shortage = requested - max_out
        if shortage > 0:
            out.append((product_id, shortage))

    return out
