from decimal import Decimal
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field

IdField = Annotated[int, Field(ge=1, description="Идентификатор продукта")]
NameField = Annotated[str, Field(min_length=1, max_length=255, description="Название продукта")]
DescriptionField = Annotated[str, Field(min_length=1, max_length=2000, description="Описание продукта")]
OutputMaterialIdField = Annotated[int, Field(ge=1, description="Идентификатор выходного материала")]
OutputQuantityField = Annotated[
    Decimal,
    Field(gt=0, max_digits=15, decimal_places=3, description="Выходное количество продукта"),
]
MaterialIdField = Annotated[int, Field(ge=1, description="Идентификатор материала")]
ResourceIdField = Annotated[int, Field(ge=1, description="Идентификатор ресурса")]
QuantityField = Annotated[Decimal, Field(gt=0, max_digits=15, decimal_places=3, description="Количество")]
CreatedAtField = Annotated[AwareDatetime, Field(description="Время создания продукта")]
IsActiveField = Annotated[bool, Field(description="Признак активности продукта")]

MaterialNameField = Annotated[str, Field(min_length=1, max_length=2000, description="Название материала")]
ResourceNameField = Annotated[str, Field(min_length=1, max_length=2000, description="Название ресурса")]

UnitIdField = Annotated[int, Field(ge=1, description="Идентификатор единицы измерения")]
UnitNameField = Annotated[str, Field(min_length=1, max_length=200, description="Название единицы измерения")]
UnitShortNameField = Annotated[str, Field(min_length=1, max_length=50, description="Краткое название единицы измерения")]


class ProductOutputMaterialUnitRead(BaseModel):
    id: UnitIdField
    name: UnitNameField
    short_name: UnitShortNameField


class ProductOutputMaterialRead(BaseModel):
    id: OutputMaterialIdField
    name: MaterialNameField
    unit: ProductOutputMaterialUnitRead
    output_quantity: OutputQuantityField


class ProductMaterialRead(BaseModel):
    id: MaterialIdField
    name: MaterialNameField
    quantity: QuantityField
    unit: ProductOutputMaterialUnitRead


class ProductResourceRead(BaseModel):
    id: ResourceIdField
    name: ResourceNameField
    quantity: QuantityField
    unit: ProductOutputMaterialUnitRead


class ProductRead(BaseModel):
    id: IdField
    name: NameField
    description: DescriptionField
    is_active: IsActiveField
    output_material: ProductOutputMaterialRead
    input_materials: list[ProductMaterialRead]
    input_resources: list[ProductResourceRead]
    created_at: CreatedAtField


class ProductMaterialPayload(BaseModel):
    material_id: MaterialIdField
    quantity: QuantityField


class ProductResourcePayload(BaseModel):
    resource_id: ResourceIdField
    quantity: QuantityField


class ProductOutputPayload(BaseModel):
    output_material_id: OutputMaterialIdField
    output_quantity: OutputQuantityField


class ProductCreate(BaseModel):
    name: NameField
    description: DescriptionField
    is_active: IsActiveField
    output_material: ProductOutputPayload
    input_materials: list[ProductMaterialPayload]
    input_resources: list[ProductResourcePayload]


class ProductCreateResponse(BaseModel):
    id: IdField


class ProductUpdate(BaseModel):
    name: NameField
    description: DescriptionField
    is_active: IsActiveField
    output_material: ProductOutputPayload
    input_materials: list[ProductMaterialPayload]
    input_resources: list[ProductResourcePayload]
