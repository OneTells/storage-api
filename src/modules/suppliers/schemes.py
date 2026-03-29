from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field

from core.schemes import Pagination

IdField = Annotated[int, Field(ge=1, description="Идентификатор поставщика")]
NameField = Annotated[str, Field(min_length=1, max_length=200, description="Название поставщика")]
IsActiveField = Annotated[bool, Field(description="Флаг активности поставщика")]
CreatedAtField = Annotated[AwareDatetime, Field(description="Время добавления поставщика")]


class SupplierRead(BaseModel):
    id: IdField
    name: NameField
    is_active: IsActiveField
    created_at: CreatedAtField


class SuppliersReadResponse(BaseModel):
    supplier: list[SupplierRead]
    pagination: Pagination
