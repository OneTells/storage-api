from decimal import Decimal
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field


class MaterialCatalogUnit(BaseModel):
    id: Annotated[int, Field(ge=1, description="Идентификатор единицы измерения")]
    name: Annotated[str, Field(min_length=1, max_length=200, description="Название единицы измерения")]
    short_name: Annotated[str, Field(min_length=1, max_length=50, description="Краткое название единицы измерения")]


class Category(BaseModel):
    id: Annotated[int, Field(ge=1, description="Идентификатор категории")]
    name: Annotated[str, Field(min_length=1, max_length=200, description="Название категории")]
    description: Annotated[str, Field(min_length=1, max_length=200, description="Описание категории")]
    created_at: Annotated[AwareDatetime, Field(description="Время создания")]


class Materials(BaseModel):
    id: Annotated[int, Field(ge=1, description="Идентификатор позиции")]
    sku: Annotated[str, Field(min_length=1, max_length=255, description="Артикул")]
    name: Annotated[str, Field(min_length=1, max_length=200, description="Название")]
    description: Annotated[str, Field(min_length=1, max_length=200, description="Описание")]
    unit: Annotated[MaterialCatalogUnit, Field(description="Единица измерения")]
    is_active: Annotated[bool, Field(description="Признак активности")]
    created_at: Annotated[AwareDatetime, Field(description="Время создания")]
    remaining_quantity: Annotated[
        Decimal,
        Field(
            ge=0,
            max_digits=18,
            decimal_places=3,
            description="Сумма остатков по партиям материала",
        ),
    ]


class CategoryMaterial(BaseModel):
    category_id: Annotated[int, Field(ge=1, description="Идентификатор категории")]
    material_id: Annotated[int, Field(ge=1, description="Идентификатор позиции")]


class CategorySubcategory(BaseModel):
    category_id: Annotated[int, Field(ge=1, description="Идентификатор категории")]
    subcategory_id: Annotated[int, Field(ge=1, description="Идентификатор подкатегории")]


class CatalogReadResponse(BaseModel):
    categories: Annotated[list[Category], Field(description="Категории")]
    materials: Annotated[list[Materials], Field(description="Позиции")]
    category_material_relations: Annotated[list[CategoryMaterial], Field(description="Связи категория–позиция")]
    category_subcategory_relations: Annotated[list[CategorySubcategory], Field(description="Связи категория-подкатегория")]
