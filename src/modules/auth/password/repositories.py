from uuid import UUID

from everbase import Connection
from sqlalchemy import Select
from sqlalchemy.dialects.postgresql import Insert

from core.models import User, UserSession


async def get_user_id(connection: Connection, username: str, password_hash: str) -> int | None:
    query = (
        Select(User.id)
        .select_from(User)
        .where(
            User.username == username,
            User.password_hash == password_hash,
            User.is_active
        )
    )

    return await connection.fetch_val(query)


async def create_session(connection: Connection, user_id: int) -> UUID:
    query = (
        Insert(UserSession)
        .values(user_id=user_id)
        .returning(UserSession.id)
    )

    return await connection.fetch_val(query)
