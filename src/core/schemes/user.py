from enum import StrEnum, auto

from pydantic import BaseModel


class UserRole(StrEnum):
    ADMIN = auto()
    USER = auto()


class UserModel(BaseModel):
    id: int
    role: UserRole
