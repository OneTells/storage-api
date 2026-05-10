from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field

from modules.products.product.schemes import OutputQuantityField, ProductOutputMaterialUnitRead


class CatalogOutputMaterial(BaseModel):
    id: Annotated[int, Field(ge=1, description="Идентификатор выходного материала")]
    name: Annotated[str, Field(min_length=1, max_length=200, description="Название материала")]
    unit: Annotated[ProductOutputMaterialUnitRead, Field(description="Единица измерения выходного материала")]
    quantity: OutputQuantityField


class Category(BaseModel):
    id: Annotated[int, Field(ge=1, description="Идентификатор категории")]
    name: Annotated[str, Field(min_length=1, max_length=200, description="Название категории")]
    description: Annotated[str, Field(min_length=1, max_length=200, description="Описание категории")]
    created_at: Annotated[AwareDatetime, Field(description="Время создания")]


class Products(BaseModel):
    id: Annotated[int, Field(ge=1, description="Идентификатор позиции")]
    name: Annotated[str, Field(min_length=1, max_length=200, description="Название")]
    description: Annotated[str, Field(min_length=1, max_length=200, description="Описание")]
    output_material: Annotated[CatalogOutputMaterial, Field(description="Выходной материал")]
    is_active: Annotated[bool, Field(description="Признак активности продукта")]
    created_at: Annotated[AwareDatetime, Field(description="Время создания")]


class CategoryProduct(BaseModel):
    category_id: Annotated[int, Field(ge=1, description="Идентификатор категории")]
    product_id: Annotated[int, Field(ge=1, description="Идентификатор позиции")]


class CategorySubcategory(BaseModel):
    category_id: Annotated[int, Field(ge=1, description="Идентификатор категории")]
    subcategory_id: Annotated[int, Field(ge=1, description="Идентификатор подкатегории")]


class CatalogReadResponse(BaseModel):
    categories: Annotated[list[Category], Field(description="Категории")]
    products: Annotated[list[Products], Field(description="Позиции")]
    category_product_relations: Annotated[list[CategoryProduct], Field(description="Связи категория–позиция")]
    category_subcategory_relations: Annotated[list[CategorySubcategory], Field(description="Связи категория-подкатегория")]
