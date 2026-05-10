from asyncpg import Record
from everbase import Connection
from sqlalchemy import Delete, func, Select, Update
from sqlalchemy.dialects.postgresql import Insert

from core.models import Product, ProductCategory, ProductCategoryProduct, ProductCategorySubcategory
from modules.products.categories.category.schemes import ProductCategoryCreate, ProductCategoryUpdate


async def create_product_category(connection: Connection, payload: ProductCategoryCreate) -> int:
    query = (
        Insert(ProductCategory)
        .values(name=payload.name, description=payload.description)
        .returning(ProductCategory.id)
    )
    return await connection.fetch_val(query)


async def get_product_category_by_id(connection: Connection, category_id: int) -> Record | None:
    query = (
        Select(
            ProductCategory.id,
            ProductCategory.name,
            ProductCategory.description,
            ProductCategory.created_at,
        )
        .where(ProductCategory.id == category_id)
    )
    return await connection.fetch_row(query)


async def update_product_category(
    connection: Connection,
    category_id: int,
    payload: ProductCategoryUpdate,
) -> None:
    query = (
        Update(ProductCategory)
        .values(name=payload.name, description=payload.description)
        .where(ProductCategory.id == category_id)
    )
    await connection.execute(query)


async def count_product_category_subcategories(connection: Connection, category_id: int) -> int:
    query = (
        Select(func.count())
        .select_from(ProductCategorySubcategory)
        .where(
            ProductCategorySubcategory.category_id == category_id
        ))
    return await connection.fetch_val(query)


async def count_product_category_products(connection: Connection, category_id: int) -> int:
    query = (
        Select(func.count())
        .select_from(ProductCategoryProduct)
        .where(
            ProductCategoryProduct.category_id == category_id
        ))
    return await connection.fetch_val(query)


async def delete_product_category(connection: Connection, category_id: int) -> None:
    await connection.execute(Delete(ProductCategory).where(ProductCategory.id == category_id))


async def product_category_exists(connection: Connection, category_id: int) -> bool:
    query = Select(
        Select(1)
        .select_from(ProductCategory)
        .where(ProductCategory.id == category_id)
        .exists()
    )

    return await connection.fetch_val(query)


async def product_exists(connection: Connection, product_id: int) -> bool:
    query = Select(
        Select(1)
        .select_from(Product)
        .where(Product.id == product_id)
        .exists()
    )

    return await connection.fetch_val(query)


async def category_product_link_exists(connection: Connection, category_id: int, product_id: int) -> bool:
    query = Select(
        Select(1)
        .select_from(ProductCategoryProduct)
        .where(
            ProductCategoryProduct.category_id == category_id,
            ProductCategoryProduct.product_id == product_id,
        )
        .exists()
    )

    return await connection.fetch_val(query)


async def insert_category_product(connection: Connection, category_id: int, product_id: int) -> None:
    query = (
        Insert(ProductCategoryProduct)
        .values(category_id=category_id, product_id=product_id)
    )

    await connection.execute(query)


async def delete_category_product(connection: Connection, category_id: int, product_id: int) -> None:
    await connection.execute(
        Delete(ProductCategoryProduct)
        .where(
            ProductCategoryProduct.category_id == category_id,
            ProductCategoryProduct.product_id == product_id,
        )
    )


async def category_subcategory_link_exists(
    connection: Connection, category_id: int, subcategory_id: int
) -> bool:
    query = Select(
        Select(1)
        .select_from(ProductCategorySubcategory)
        .where(
            ProductCategorySubcategory.category_id == category_id,
            ProductCategorySubcategory.subcategory_id == subcategory_id,
        )
        .exists()
    )
    return await connection.fetch_val(query)


async def insert_category_subcategory(connection: Connection, category_id: int, subcategory_id: int) -> None:
    query = (
        Insert(ProductCategorySubcategory)
        .values(
            category_id=category_id,
            subcategory_id=subcategory_id,
        )
    )

    await connection.execute(query)


async def delete_category_subcategory(connection: Connection, category_id: int, subcategory_id: int) -> None:
    await connection.execute(
        Delete(ProductCategorySubcategory)
        .where(
            ProductCategorySubcategory.category_id == category_id,
            ProductCategorySubcategory.subcategory_id == subcategory_id,
        )
    )
