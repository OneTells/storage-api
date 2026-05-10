from decimal import Decimal
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field

IdField = Annotated[int, Field(ge=1, description="Идентификатор материала")]
SkuField = Annotated[str, Field(min_length=1, max_length=255, description="Артикул материала")]
UnitIdField = Annotated[int, Field(ge=1, description="Идентификатор единицы измерения")]
NameField = Annotated[str, Field(min_length=1, max_length=200, description="Название материала")]
DescriptionField = Annotated[str, Field(max_length=1000, description="Описание материала")]
IsActiveField = Annotated[bool, Field(description="Флаг активности материала")]
CreatedAtField = Annotated[AwareDatetime, Field(description="Время создания материала")]


class MaterialWarehouseStock(BaseModel):
    warehouse_id: Annotated[int, Field(ge=1, description="Идентификатор склада")]
    warehouse_name: Annotated[str, Field(min_length=1, max_length=200, description="Название склада")]
    warehouse_is_active: Annotated[bool, Field(description="Признак активности склада")]
    remaining_quantity: Annotated[
        Decimal,
        Field(
            ge=0,
            max_digits=18,
            decimal_places=3,
            description="Остаток материала на этом складе (сумма remaining по партиям)",
        ),
    ]


class MaterialRead(BaseModel):
    id: IdField
    sku: SkuField
    name: NameField
    description: DescriptionField
    unit_id: UnitIdField
    is_active: IsActiveField
    created_at: CreatedAtField
    warehouse_stocks: Annotated[
        list[MaterialWarehouseStock],
        Field(description="Остатки материала по складам (только склады, где есть партии этого материала)"),
    ]


class MaterialCreate(BaseModel):
    sku: SkuField
    name: NameField
    description: DescriptionField
    unit_id: UnitIdField
    is_active: IsActiveField


class MaterialCreateResponse(BaseModel):
    id: IdField


class MaterialUpdate(BaseModel):
    sku: SkuField
    name: NameField
    description: DescriptionField
    unit_id: UnitIdField
    is_active: IsActiveField
