from pydantic import BaseModel

from modules.warehouses.schemes import CommentField, IdField, IsActiveField, NameField


class WarehouseCreate(BaseModel):
    name: NameField
    comment: CommentField
    is_active: IsActiveField


class WarehouseCreateResponse(BaseModel):
    id: IdField


class WarehouseUpdate(BaseModel):
    name: NameField
    comment: CommentField
    is_active: IsActiveField
