from pydantic import BaseModel

from modules.roles.schemes import NameField


class RoleCreate(BaseModel):
    name: NameField


class RoleCreateResponse(BaseModel):
    id: int


class RoleUpdate(BaseModel):
    name: NameField
