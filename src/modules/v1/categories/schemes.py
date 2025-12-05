from typing import Annotated

from fastapi import Path
from pydantic import AwareDatetime, BaseModel, Field

CategoryIdType = Annotated[int, Path(ge=1, description="Идентификатор категории")]

IdField = Annotated[int, Field(ge=1, description="Идентификатор категории")]
NameField = Annotated[str, Field(min_length=1, max_length=200, description="Название категории")]
DescriptionField = Annotated[str, Field(min_length=1, max_length=200, description="Описание категории")]
CreatedAtField = Annotated[AwareDatetime, Field(description="Время создания категории")]


class CategoryCreate(BaseModel):
    name: NameField
    description: DescriptionField


class CategoryCreateResponse(BaseModel):
    id: IdField


class CategoryRead(BaseModel):
    id: IdField
    name: NameField
    description: DescriptionField

    created_at: CreatedAtField


class CategoryUpdate(BaseModel):
    name: NameField
    description: DescriptionField
