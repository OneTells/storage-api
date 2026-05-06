from decimal import Decimal
from typing import Annotated, Literal

from pydantic import AwareDatetime, BaseModel, Field, TypeAdapter

from core.models import ResourceType
from core.schemes import Pagination

IdField = Annotated[int, Field(ge=1, description="Идентификатор ресурса")]
TypeField = Annotated[ResourceType, Field(description="Тип ресурса")]
NameField = Annotated[str, Field(min_length=1, max_length=255, description="Наименование ресурса")]
UnitIdField = Annotated[int, Field(ge=1, description="Идентификатор единицы измерения")]
FixedRateField = Annotated[
    Decimal | None,
    Field(default=None, ge=0, max_digits=15, decimal_places=2, description="Фиксированная ставка")
]
InitialAmountField = Annotated[
    Decimal | None,
    Field(default=None, ge=0, max_digits=15, decimal_places=2, description="Первоначальная стоимость")
]
ServiceLifeField = Annotated[
    Decimal | None,
    Field(default=None, ge=0, max_digits=15, decimal_places=2, description="Срок службы")
]
RequiredUnitIdField = Annotated[int, Field(ge=1, description="Идентификатор единицы измерения")]
RequiredFixedRateField = Annotated[
    Decimal,
    Field(ge=0, max_digits=15, decimal_places=2, description="Фиксированная ставка")
]
RequiredInitialAmountField = Annotated[
    Decimal,
    Field(ge=0, max_digits=15, decimal_places=2, description="Первоначальная стоимость")
]
RequiredServiceLifeField = Annotated[
    Decimal,
    Field(ge=0, max_digits=15, decimal_places=2, description="Срок службы")
]
CreatedAtField = Annotated[AwareDatetime, Field(description="Время создания ресурса")]


class ResourceReadBase(BaseModel):
    id: IdField
    type: TypeField
    name: NameField
    unit_id: UnitIdField
    created_at: CreatedAtField


class ResourceReadFixedRate(ResourceReadBase):
    type: Literal[ResourceType.FIXED_RATE]

    fixed_rate: FixedRateField


class ResourceReadDepreciation(ResourceReadBase):
    type: Literal[ResourceType.DEPRECIATION]

    initial_amount: InitialAmountField
    service_life: ServiceLifeField


ResourceRead = Annotated[
    ResourceReadFixedRate |
    ResourceReadDepreciation,
    Field(discriminator="type")
]

resource_read_adapter = TypeAdapter(ResourceRead)


class ResourcesReadResponse(BaseModel):
    resources: list[ResourceRead]
    pagination: Pagination
