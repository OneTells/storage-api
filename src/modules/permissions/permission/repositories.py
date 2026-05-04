from asyncpg import Record
from everbase import Connection
from sqlalchemy import Delete, Select, Update
from sqlalchemy.dialects.postgresql import Insert

from core.models import Permission


async def get_permission_by_id(connection: Connection, permission_id: int) -> Record | None:
    query = (
        Select(Permission.id, Permission.name, Permission.codename)
        .where(Permission.id == permission_id)
    )

    return await connection.fetch_row(query)


async def exist_permission_by_name(connection: Connection, name: str) -> bool:
    query = (
        Select(
            Select(1)
            .select_from(Permission)
            .where(Permission.name == name)
            .exists()
        )
    )

    return await connection.fetch_val(query)


async def exist_permission_by_codename(connection: Connection, codename: str) -> bool:
    query = (
        Select(
            Select(1)
            .select_from(Permission)
            .where(Permission.codename == codename)
            .exists()
        )
    )

    return await connection.fetch_val(query)


async def create_permission(connection: Connection, name: str, codename: str) -> int:
    query = (
        Insert(Permission)
        .values(name=name, codename=codename)
        .returning(Permission.id)
    )

    return await connection.fetch_val(query)


async def update_permission(connection: Connection, permission_id: int, name: str, codename: str) -> None:
    query = (
        Update(Permission)
        .values(name=name, codename=codename)
        .where(Permission.id == permission_id)
    )

    await connection.execute(query)


async def delete_permission(connection: Connection, permission_id: int) -> None:
    query = (
        Delete(Permission)
        .where(Permission.id == permission_id)
    )

    await connection.execute(query)
