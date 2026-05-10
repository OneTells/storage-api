from asyncpg import Record
from everbase import Connection
from sqlalchemy import Delete, func, Select, Update
from sqlalchemy.dialects.postgresql import Insert

from core.models import Material, MaterialCategory, MaterialCategoryMaterial, MaterialCategorySubcategory
from modules.materials.categories.category.schemes import CategoryCreate, CategoryUpdate


async def create_material_category(connection: Connection, payload: CategoryCreate) -> int:
    query = (
        Insert(MaterialCategory)
        .values(name=payload.name, description=payload.description)
        .returning(MaterialCategory.id)
    )
    return await connection.fetch_val(query)


async def get_material_category_by_id(connection: Connection, category_id: int) -> Record | None:
    query = (
        Select(MaterialCategory.id, MaterialCategory.name, MaterialCategory.description, MaterialCategory.created_at)
        .where(MaterialCategory.id == category_id)
    )
    return await connection.fetch_row(query)


async def update_material_category(
    connection: Connection,
    category_id: int,
    payload: CategoryUpdate,
) -> None:
    query = (
        Update(MaterialCategory)
        .values(name=payload.name, description=payload.description)
        .where(MaterialCategory.id == category_id)
    )
    await connection.execute(query)


async def count_material_category_subcategories(connection: Connection, category_id: int) -> int:
    query = (
        Select(func.count())
        .select_from(MaterialCategorySubcategory)
        .where(
            MaterialCategorySubcategory.category_id == category_id
        )
    )

    return await connection.fetch_val(query)


async def count_material_category_materials(connection: Connection, category_id: int) -> int:
    query = (
        Select(func.count())
        .select_from(MaterialCategoryMaterial)
        .where(
            MaterialCategoryMaterial.category_id == category_id
        )
    )

    return await connection.fetch_val(query)


async def delete_material_category(connection: Connection, category_id: int) -> None:
    await connection.execute(Delete(MaterialCategory).where(MaterialCategory.id == category_id))


async def material_exists(connection: Connection, material_id: int) -> bool:
    query = Select(
        Select(1)
        .select_from(Material)
        .where(Material.id == material_id)
        .exists()
    )
    return await connection.fetch_val(query)


async def category_material_link_exists(connection: Connection, category_id: int, material_id: int) -> bool:
    query = Select(
        Select(1)
        .select_from(MaterialCategoryMaterial)
        .where(
            MaterialCategoryMaterial.category_id == category_id,
            MaterialCategoryMaterial.material_id == material_id,
        )
        .exists()
    )
    return await connection.fetch_val(query)


async def insert_category_material(connection: Connection, category_id: int, material_id: int) -> None:
    query = (
        Insert(MaterialCategoryMaterial)
        .values(category_id=category_id, material_id=material_id)
    )

    await connection.execute(query)


async def delete_category_material(connection: Connection, category_id: int, material_id: int) -> None:
    await connection.execute(
        Delete(MaterialCategoryMaterial)
        .where(
            MaterialCategoryMaterial.category_id == category_id,
            MaterialCategoryMaterial.material_id == material_id,
        )
    )


async def material_category_exists(connection: Connection, category_id: int) -> bool:
    query = Select(
        Select(1)
        .select_from(MaterialCategory)
        .where(MaterialCategory.id == category_id)
        .exists()
    )
    return await connection.fetch_val(query)


async def category_subcategory_link_exists(
    connection: Connection, category_id: int, subcategory_id: int
) -> bool:
    query = Select(
        Select(1)
        .select_from(MaterialCategorySubcategory)
        .where(
            MaterialCategorySubcategory.category_id == category_id,
            MaterialCategorySubcategory.subcategory_id == subcategory_id,
        )
        .exists()
    )
    return await connection.fetch_val(query)


async def insert_category_subcategory(
    connection: Connection, category_id: int, subcategory_id: int
) -> None:
    query = (
        Insert(MaterialCategorySubcategory)
        .values(
            category_id=category_id,
            subcategory_id=subcategory_id,
        )
    )
    await connection.execute(query)


async def delete_category_subcategory(
    connection: Connection, category_id: int, subcategory_id: int
) -> None:
    await connection.execute(
        Delete(MaterialCategorySubcategory)
        .where(
            MaterialCategorySubcategory.category_id == category_id,
            MaterialCategorySubcategory.subcategory_id == subcategory_id,
        )
    )
