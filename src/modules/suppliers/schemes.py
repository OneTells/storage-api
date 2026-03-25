from typing import Annotated

from fastapi import Path
from pydantic import BaseModel, AwareDatetime, Field



IdField = Annotated[int, Field(ge=1, description="Идентификатор поставщика")]
NameField = Annotated[str, Field(min_length=1, max_length=200, description="Название поставщика")]
IsActiveField = Annotated[bool, Field(description="Флаг активности поставщика")]
CreatedAtField = Annotated[AwareDatetime, Field(description="Время добавления поставщика")]


class SupplierCreate(BaseModel):
    name: NameField
    is_active: IsActiveField


class SupplierCreateResponse(BaseModel):
    id: IdField


class SupplierRead(BaseModel):
    id: IdField
    name: NameField
    is_active: IsActiveField
    created_at: CreatedAtField


class SupplierUpdate(BaseModel):
    name: NameField
    is_active: IsActiveField
