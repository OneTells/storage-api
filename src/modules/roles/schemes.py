from typing import Annotated

from pydantic import BaseModel, Field

from core.schemes import Pagination

IdField = Annotated[int, Field(ge=1, description="Идентификатор роли")]
NameField = Annotated[str, Field(min_length=1, max_length=100, description="Название роли")]
DescriptionField = Annotated[str, Field(min_length=1, max_length=500, description="Описание роли")]
PermissionIdField = Annotated[int, Field(ge=1, description="Идентификатор разрешения")]
PermissionNameField = Annotated[str, Field(min_length=1, max_length=255, description="Название разрешения")]
PermissionCodenameField = Annotated[str, Field(min_length=1, max_length=255, description="Кодовое имя разрешения")]


class RolePermission(BaseModel):
    id: PermissionIdField
    name: PermissionNameField
    codename: PermissionCodenameField


class RoleRead(BaseModel):
    id: IdField
    name: NameField
    description: DescriptionField
    permissions: list[RolePermission]


class RolesReadResponse(BaseModel):
    roles: list[RoleRead]
    pagination: Pagination
