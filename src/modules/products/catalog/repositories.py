from asyncpg import Record
from everbase import Connection
from sqlalchemy import Select
from sqlalchemy.orm import aliased

from core.models import (
    Material,
    Product,
    ProductCategory,
    ProductCategoryProduct,
    ProductCategorySubcategory,
    Unit,
)


async def fetch_catalog_categories(connection: Connection) -> list[Record]:
    query = (
        Select(
            ProductCategory.id,
            ProductCategory.name,
            ProductCategory.description,
            ProductCategory.created_at,
        )
        .order_by(ProductCategory.id)
    )

    return await connection.fetch(query)


async def fetch_catalog_category_product_links(connection: Connection, product_ids: list[int]) -> list[Record]:
    query = (
        Select(ProductCategoryProduct.category_id, ProductCategoryProduct.product_id)
        .where(ProductCategoryProduct.product_id.in_(product_ids))
    )

    return await connection.fetch(query)


async def fetch_catalog_category_subcategory_links(connection: Connection) -> list[Record]:
    query = Select(ProductCategorySubcategory.category_id, ProductCategorySubcategory.subcategory_id)
    return await connection.fetch(query)


async def fetch_catalog_products(connection: Connection, is_active_products: bool | None) -> list[Record]:
    output_unit = aliased(Unit)
    query = (
        Select(
            Product.id,
            Product.name,
            Product.description,
            Product.is_active,
            Product.created_at,
            Product.output_quantity.label("quantity"),
            Material.id.label("output_material_id"),
            Material.name.label("output_material_name"),
            output_unit.id.label("output_material_unit_id"),
            output_unit.name.label("output_material_unit_name"),
            output_unit.short_name.label("output_material_unit_short_name"),
        )
        .select_from(Product)
        .join(Material, Product.output_material_id == Material.id)
        .join(output_unit, output_unit.id == Material.unit_id)
        .order_by(Product.id)
    )

    if is_active_products is not None:
        query = query.where(Product.is_active == is_active_products)

    return await connection.fetch(query)
