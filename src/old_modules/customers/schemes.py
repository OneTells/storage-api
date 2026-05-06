from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field

from core.schemes import Pagination

IdField = Annotated[int, Field(ge=1, description="Идентификатор клиента")]
NameField = Annotated[str, Field(min_length=1, max_length=200, description="Название клиента")]
IsActiveField = Annotated[bool, Field(description="Флаг активности клиента")]
CreatedAtField = Annotated[AwareDatetime, Field(description="Время создания клиента")]


class CustomerRead(BaseModel):
    id: IdField
    name: NameField
    is_active: IsActiveField
    created_at: CreatedAtField


class CustomersReadResponse(BaseModel):
    customers: list[CustomerRead]
    pagination: Pagination
