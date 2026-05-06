from typing import Annotated
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, Field

from modules.users.schemes import IsActiveField, NameField, PasswordField, UsernameField

SessionIdField = Annotated[UUID, Field(description="Идентификатор сессии")]
SessionCreatedAtField = Annotated[AwareDatetime, Field(description="Время создания сессии")]
SessionDeactivatedAtField = Annotated[AwareDatetime | None, Field(description="Время деактивации сессии")]


class UserCreate(BaseModel):
    name: NameField
    username: UsernameField
    password: PasswordField
    is_active: IsActiveField


class UserCreateResponse(BaseModel):
    id: int


class UserUpdate(BaseModel):
    name: NameField
    username: UsernameField
    is_active: IsActiveField


class UserChangePassword(BaseModel):
    new_password: PasswordField


class UserSession(BaseModel):
    id: SessionIdField
    is_active: IsActiveField
    created_at: SessionCreatedAtField
    deactivated_at: SessionDeactivatedAtField


class UserSessionsResponse(BaseModel):
    sessions: list[UserSession]
