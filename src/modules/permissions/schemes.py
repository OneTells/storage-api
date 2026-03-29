from typing import Annotated

from pydantic import BaseModel, Field

from core.schemes import Pagination

IdField = Annotated[int, Field(ge=1, description="Идентификатор разрешения")]
NameField = Annotated[str, Field(min_length=1, max_length=255, description="Название разрешения")]
CodenameField = Annotated[str, Field(min_length=1, max_length=255, description="Кодовое имя разрешения")]


class PermissionRead(BaseModel):
    id: IdField
    name: NameField
    codename: CodenameField


class PermissionsReadResponse(BaseModel):
    permissions: list[PermissionRead]
    pagination: Pagination
