from typing import Annotated, Literal

from pydantic import BaseModel, Field

from core.models import ResourceType
from modules.resources.schemes import (
    IdField, NameField, RequiredFixedRateField, RequiredInitialAmountField, RequiredServiceLifeField, RequiredUnitIdField
)


class ResourceCreateFixedRate(BaseModel):
    type: Literal[ResourceType.FIXED_RATE]

    name: NameField
    unit_id: RequiredUnitIdField
    fixed_rate: RequiredFixedRateField
    initial_amount: Literal[None] = None
    service_life: Literal[None] = None


class ResourceCreateDepreciation(BaseModel):
    type: Literal[ResourceType.DEPRECIATION]

    name: NameField
    unit_id: RequiredUnitIdField
    fixed_rate: Literal[None] = None
    initial_amount: RequiredInitialAmountField
    service_life: RequiredServiceLifeField


ResourceCreate = Annotated[
    ResourceCreateFixedRate | ResourceCreateDepreciation,
    Field(discriminator="type")
]


class ResourceCreateResponse(BaseModel):
    id: IdField


ResourceUpdate = Annotated[
    ResourceCreateFixedRate | ResourceCreateDepreciation,
    Field(discriminator="type")
]
