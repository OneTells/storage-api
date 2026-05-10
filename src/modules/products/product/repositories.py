from asyncpg import Record
from everbase import Connection
from sqlalchemy import Delete, func, Select, Update
from sqlalchemy.orm import aliased
from sqlalchemy.dialects.postgresql import Insert

from core.models import Material, Product, ProductCategoryProduct, ProductMaterial, ProductResource, Resource, Unit
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
