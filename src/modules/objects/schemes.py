from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field

from core.schemes import Pagination

IdField = Annotated[int, Field(ge=1, description="Идентификатор объекта")]
NameField = Annotated[str, Field(min_length=1, max_length=200, description="Название объекта")]
DescriptionField = Annotated[str, Field(max_length=1000, description="Описание объекта")]
IsActiveField = Annotated[bool, Field(description="Флаг активности объекта")]
CreatedAtField = Annotated[AwareDatetime, Field(description="Время создания объекта")]


class ObjectRead(BaseModel):
    id: IdField
    name: NameField
    description: DescriptionField
    is_active: IsActiveField
    created_at: CreatedAtField


class ObjectsReadResponse(BaseModel):
    objects: list[ObjectRead]
    pagination: Pagination
