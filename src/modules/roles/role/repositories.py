from asyncpg import Record
from everbase import Connection
from sqlalchemy import Delete, func, Select, Update
from sqlalchemy.dialects.postgresql import Insert

from core.models import Permission, Role, RolePermission


async def get_role_by_id(connection: Connection, role_id: int) -> Record | None:
    query = (
        Select(
            Role.id,
            Role.name,
            Role.description,
            func.coalesce(
                func.array_agg(
                    func.jsonb_build_object(
                        'id', Permission.id,
                        'name', Permission.name,
                        'codename', Permission.codename
                    )
                ).filter(Permission.id.isnot(None)),
                []
            ).label('permissions')
        )
        .outerjoin(RolePermission, Role.id == RolePermission.role_id)
        .outerjoin(Permission, Permission.id == RolePermission.permission_id)
        .where(Role.id == role_id)
        .group_by(Role.id, Role.name, Role.description)
    )

    return await connection.fetch_row(query)


async def exist_role_by_name(connection: Connection, name: str) -> bool:
    query = (
        Select(
            Select(1)
            .select_from(Role)
            .where(Role.name == name)
            .exists()
        )
    )

    return await connection.fetch_val(query)


async def exist_role_by_id(connection: Connection, role_id: int) -> bool:
    query = (
        Select(
            Select(1)
            .select_from(Role)
            .where(Role.id == role_id)
            .exists()
        )
    )

    return await connection.fetch_val(query)


async def exist_permission_by_id(connection: Connection, permission_id: int) -> bool:
    query = (
        Select(
            Select(1)
            .select_from(Permission)
            .where(Permission.id == permission_id)
            .exists()
        )
    )

    return await connection.fetch_val(query)


async def create_role(connection: Connection, name: str, description: str) -> int:
    query = (
        Insert(Role)
        .values(name=name, description=description)
        .returning(Role.id)
    )

    return await connection.fetch_val(query)


async def update_role(connection: Connection, role_id: int, name: str, description: str) -> None:
    query = (
        Update(Role)
        .values(name=name, description=description)
        .where(Role.id == role_id)
    )

    await connection.execute(query)


async def delete_role(connection: Connection, role_id: int) -> None:
    query = (
        Delete(Role)
        .where(Role.id == role_id)
    )

    await connection.execute(query)


async def assign_permission_to_role(connection: Connection, role_id: int, permission_id: int) -> None:
    query = (
        Insert(RolePermission)
        .values(role_id=role_id, permission_id=permission_id)
        .on_conflict_do_nothing(index_elements=['role_id', 'permission_id'])
    )

    await connection.execute(query)


async def remove_permission_from_role(connection: Connection, role_id: int, permission_id: int) -> None:
    query = (
        Delete(RolePermission)
        .where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id
        )
    )

    await connection.execute(query)
