from typing import Annotated

from pydantic import BaseModel, Field

from core.schemes import Pagination

IdField = Annotated[int, Field(ge=1, description="Идентификатор роли")]
NameField = Annotated[str, Field(min_length=1, max_length=100, description="Название роли")]


class RoleRead(BaseModel):
    id: IdField
    name: NameField


class RolesReadResponse(BaseModel):
    roles: list[RoleRead]
    pagination: Pagination
