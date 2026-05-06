from asyncpg import Record
from everbase import Connection
from sqlalchemy import Delete, func, Select, Update
from sqlalchemy.dialects.postgresql import Insert

from core.models import Permission, Role, RolePermission, User, UserRole, UserSession


async def get_user_by_id(connection: Connection, user_id: int) -> Record | None:
    query = (
        Select(
            User.id,
            User.name,
            User.username,
            User.is_active,
            User.created_at,
            func.coalesce(
                func.array_agg(
                    func.distinct(
                        func.jsonb_build_object(
                            'id', Role.id,
                            'name', Role.name,
                            'description', Role.description
                        )
                    )
                ).filter(Role.id.isnot(None)),
                []
            ).label('roles'),
            func.coalesce(
                func.array_agg(
                    func.distinct(
                        func.jsonb_build_object(
                            'id', Permission.id,
                            'name', Permission.name,
                            'codename', Permission.codename
                        )
                    )
                ).filter(Permission.id.isnot(None)),
                []
            ).label('permissions')
        )
        .outerjoin(UserRole, User.id == UserRole.user_id)
        .outerjoin(Role, Role.id == UserRole.role_id)
        .outerjoin(RolePermission, Role.id == RolePermission.role_id)
        .outerjoin(Permission, Permission.id == RolePermission.permission_id)
        .where(User.id == user_id)
        .group_by(User.id, User.name, User.username, User.is_active, User.created_at)
    )

    return await connection.fetch_row(query)


async def exist_user_by_username(connection: Connection, username: str) -> bool:
    query = (
        Select(
            Select(1)
            .select_from(User)
            .where(User.username == username)
            .exists()
        )
    )

    return await connection.fetch_val(query)


async def exist_user_by_id(connection: Connection, user_id: int) -> bool:
    query = (
        Select(
            Select(1)
            .select_from(User)
            .where(User.id == user_id)
            .exists()
        )
    )

    return await connection.fetch_val(query)


async def get_user_username(connection: Connection, user_id: int) -> str | None:
    query = (
        Select(User.username)
        .where(User.id == user_id)
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


async def create_user(
    connection: Connection,
    name: str,
    username: str,
    password_hash: str,
    is_active: bool
) -> int:
    query = (
        Insert(User)
        .values(name=name, username=username, password_hash=password_hash, is_active=is_active)
        .returning(User.id)
    )

    return await connection.fetch_val(query)


async def update_user(
    connection: Connection,
    user_id: int,
    name: str,
    username: str,
    is_active: bool
) -> None:
    query = (
        Update(User)
        .values(name=name, username=username, is_active=is_active)
        .where(User.id == user_id)
    )

    await connection.execute(query)


async def delete_user(connection: Connection, user_id: int) -> None:
    query = (
        Delete(User)
        .where(User.id == user_id)
    )

    await connection.execute(query)


async def assign_role_to_user(connection: Connection, user_id: int, role_id: int) -> None:
    query = (
        Insert(UserRole)
        .values(user_id=user_id, role_id=role_id)
        .on_conflict_do_nothing(index_elements=['user_id', 'role_id'])
    )

    await connection.execute(query)


async def remove_role_from_user(connection: Connection, user_id: int, role_id: int) -> None:
    query = (
        Delete(UserRole)
        .where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
        )
    )

    await connection.execute(query)


async def change_user_password(connection: Connection, user_id: int, new_password_hash: str) -> None:
    query = (
        Update(User)
        .values(password_hash=new_password_hash)
        .where(User.id == user_id)
    )

    await connection.execute(query)


async def get_user_sessions(connection: Connection, user_id: int, sessions_limit: int = 10) -> list[Record]:
    query = (
        Select(UserSession.id, UserSession.is_active, UserSession.created_at, UserSession.deactivated_at)
        .where(UserSession.user_id == user_id)
        .order_by(UserSession.created_at.desc())
        .limit(sessions_limit)
    )

    return await connection.fetch(query)


async def exist_user_session(connection: Connection, user_id: int, session_id: str) -> bool:
    query = (
        Select(
            Select(1)
            .select_from(UserSession)
            .where(
                UserSession.user_id == user_id,
                UserSession.id == session_id,
                UserSession.is_active == True,
            )
            .exists()
        )
    )

    return await connection.fetch_val(query)


async def deactivate_user_session(connection: Connection, user_id: int, session_id: str) -> None:
    query = (
        Update(UserSession)
        .values(
            is_active=False,
            deactivated_at=func.now()
        )
        .where(
            UserSession.user_id == user_id,
            UserSession.id == session_id,
            UserSession.is_active == True,
        )
    )

    await connection.execute(query)
