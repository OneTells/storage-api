from pydantic import BaseModel

from modules.permissions.schemes import CodenameField, NameField


class PermissionCreate(BaseModel):
    name: NameField
    codename: CodenameField


class PermissionCreateResponse(BaseModel):
    id: int


class PermissionUpdate(BaseModel):
    name: NameField
    codename: CodenameField
