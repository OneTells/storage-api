from pydantic import BaseModel

from modules.suppliers.schemes import IdField, IsActiveField, NameField


class SupplierCreate(BaseModel):
    name: NameField
    is_active: IsActiveField


class SupplierCreateResponse(BaseModel):
    id: IdField


class SupplierUpdate(BaseModel):
    name: NameField
    is_active: IsActiveField
