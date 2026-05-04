from pydantic import BaseModel

from modules.roles.schemes import DescriptionField, NameField


class RoleCreate(BaseModel):
    name: NameField
    description: DescriptionField


class RoleCreateResponse(BaseModel):
    id: int


class RoleUpdate(BaseModel):
    name: NameField
    description: DescriptionField
