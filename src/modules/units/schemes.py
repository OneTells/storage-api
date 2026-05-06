from decimal import Decimal
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field

from core.models import UnitCategoryEnum
from core.schemes import Pagination

IdField = Annotated[int, Field(ge=1, description="Идентификатор единицы измерения")]
CategoryField = Annotated[UnitCategoryEnum, Field(description="Категория единицы измерения")]
NameField = Annotated[str, Field(min_length=1, max_length=200, description="Название единицы измерения")]
ShortNameField = Annotated[str, Field(min_length=1, max_length=50, description="Краткое название единицы измерения")]
ConversionFactorField = Annotated[
    Decimal,
    Field(gt=0, max_digits=20, decimal_places=10, description="Коэффициент конвертации")
]
IsBaseField = Annotated[bool, Field(description="Флаг базовой единицы измерения")]
CreatedAtField = Annotated[AwareDatetime, Field(description="Время создания единицы измерения")]


class UnitRead(BaseModel):
    id: IdField
    category: CategoryField
    name: NameField
    short_name: ShortNameField
    conversion_factor: ConversionFactorField
    is_base: IsBaseField
    created_at: CreatedAtField


class UnitsReadResponse(BaseModel):
    units: list[UnitRead]
    pagination: Pagination
