from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field

from core.schemes import Pagination

IdField = Annotated[int, Field(ge=1, description="Идентификатор категории")]
NameField = Annotated[str, Field(min_length=1, max_length=200, description="Название категории")]
DescriptionField = Annotated[str, Field(min_length=1, max_length=1000, description="Описание категории")]
CreatedAtField = Annotated[AwareDatetime, Field(description="Время создания категории")]


class ProductCategoryCreate(BaseModel):
    name: NameField
    description: DescriptionField


class ProductCategoryCreateResponse(BaseModel):
    id: IdField


class ProductCategoryRead(BaseModel):
    id: IdField
    name: NameField
    description: DescriptionField
    created_at: CreatedAtField


class ProductCategoryUpdate(BaseModel):
    name: NameField
    description: DescriptionField


class ProductCategoriesReadResponse(BaseModel):
    product_categories: list[ProductCategoryRead]
    pagination: Pagination


class ProductSubcategoriesReadResponse(BaseModel):
    subcategories: list[ProductCategoryRead]
    pagination: Pagination
