from uuid import UUID

from pydantic import BaseModel


class UserModel(BaseModel):
    id: int
    session_id: UUID
    permissions: list[str]
