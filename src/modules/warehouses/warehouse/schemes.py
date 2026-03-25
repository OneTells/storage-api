from pydantic import BaseModel

from modules.warehouses.schemes import AddressField, IdField, IsActiveField, NameField


class WarehouseCreate(BaseModel):
    name: NameField
    address: AddressField
    is_active: IsActiveField


class WarehouseCreateResponse(BaseModel):
    id: IdField


class WarehouseUpdate(BaseModel):
    name: NameField
    address: AddressField
    is_active: IsActiveField
