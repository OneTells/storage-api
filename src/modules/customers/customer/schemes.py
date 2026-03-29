from pydantic import BaseModel

from modules.customers.schemes import IdField, IsActiveField, NameField


class CustomerCreate(BaseModel):
    name: NameField
    is_active: IsActiveField


class CustomerCreateResponse(BaseModel):
    id: IdField


class CustomerUpdate(BaseModel):
    name: NameField
    is_active: IsActiveField
