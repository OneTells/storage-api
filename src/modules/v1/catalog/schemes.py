from typing import Annotated

from pydantic import BaseModel, Field


class Category(BaseModel):
    id: Annotated[int, Field(ge=1, description="Идентификатор категории")]
    name: Annotated[str, Field(min_length=1, max_length=200, description="Название категории")]
    description: Annotated[str, Field(min_length=1, max_length=200, description="Описание категории")]


class Objects(BaseModel):
    id: Annotated[int, Field(ge=1, description="Идентификатор объекта")]
    name: Annotated[str, Field(min_length=1, max_length=200, description="Название объекта")]
    description: Annotated[str, Field(min_length=1, max_length=200, description="Описание объекта")]
    is_active: Annotated[bool, Field(description="Активность объекта")]


class CategoryObject(BaseModel):
    category_id: Annotated[int, Field(ge=1, description="Идентификатор категории")]
    object_id: Annotated[int, Field(ge=1, description="Идентификатор объекта")]


class CategorySubcategory(BaseModel):
    category_id: Annotated[int, Field(ge=1, description="Идентификатор категории")]
    subcategory_id: Annotated[int, Field(ge=1, description="Идентификатор подкатегории")]


class CatalogRead(BaseModel):
    categories: Annotated[list[Category], Field(description="Список категорий")]
    objects: Annotated[list[Objects], Field(description="Список объектов")]
    category_object_relations: Annotated[list[CategoryObject], Field(description="Связи категория-объект")]
    category_subcategory_relations: Annotated[list[CategorySubcategory], Field(description="Связи категория-подкатегория")]
