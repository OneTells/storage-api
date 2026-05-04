from uuid import UUID

from everbase import Connection
from sqlalchemy import func, Update

from core.models import UserSession


async def deactivate_session(connection: Connection, session_id: UUID) -> None:
    query = (
        Update(UserSession)
        .where(UserSession.id == session_id)
        .values(is_active=False, deactivated_at=func.now())
    )

    await connection.execute(query)
