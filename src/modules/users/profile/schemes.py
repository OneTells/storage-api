from typing import Annotated
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, Field

from modules.users.schemes import CreatedAtField, IdField, IsActiveField, NameField, UsernameField

SessionIdField = Annotated[UUID, Field(description="Идентификатор сессии")]
RoleIdField = Annotated[int, Field(ge=1, description="Идентификатор роли")]
RoleNameField = Annotated[str, Field(min_length=1, max_length=255, description="Название роли")]
RoleDescriptionField = Annotated[str, Field(min_length=1, max_length=500, description="Описание роли")]
PermissionIdField = Annotated[int, Field(ge=1, description="Идентификатор разрешения")]
PermissionNameField = Annotated[str, Field(min_length=1, max_length=255, description="Название разрешения")]
PermissionCodenameField = Annotated[str, Field(min_length=1, max_length=255, description="Кодовое имя разрешения")]
SessionCreatedAtField = Annotated[AwareDatetime, Field(description="Время создания сессии")]
SessionDeactivatedAtField = Annotated[AwareDatetime | None, Field(description="Время деактивации сессии")]


class UserRole(BaseModel):
    id: RoleIdField
    name: RoleNameField
    description: RoleDescriptionField


class UserPermission(BaseModel):
    id: PermissionIdField
    name: PermissionNameField
    codename: PermissionCodenameField


class UserSession(BaseModel):
    id: SessionIdField
    is_active: IsActiveField
    created_at: SessionCreatedAtField
    deactivated_at: SessionDeactivatedAtField


class ProfileRead(BaseModel):
    id: IdField
    name: NameField
    username: UsernameField
    is_active: IsActiveField
    created_at: CreatedAtField
    roles: list[UserRole]
    permissions: list[UserPermission]
    sessions: list[UserSession]
