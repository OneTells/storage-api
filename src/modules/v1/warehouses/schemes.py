from typing import Annotated

from fastapi import Path
from pydantic import BaseModel, AwareDatetime, Field

WarehouseIdType = Annotated[int, Path(ge=1, description="Идентификатор склада")]

IdField = Annotated[int, Field(ge=1, description="Идентификатор склада")]
NameField = Annotated[str, Field(min_length=1, max_length=200, description="Название склада")]
AddressField = Annotated[str, Field(min_length=1, max_length=200, description="Адрес склада")]
IsActiveField = Annotated[bool, Field(description="Флаг активности склада")]
CreatedAtField = Annotated[AwareDatetime, Field(description="Время создания склада")]


class WarehouseCreate(BaseModel):
    name: NameField
    address: AddressField
    is_active: IsActiveField


class WarehouseCreateResponse(BaseModel):
    id: IdField


class WarehouseRead(BaseModel):
    id: IdField
    name: NameField
    address: AddressField
    is_active: IsActiveField
    created_at: CreatedAtField


class WarehouseUpdate(BaseModel):
    name: NameField
    address: AddressField
    is_active: IsActiveField
