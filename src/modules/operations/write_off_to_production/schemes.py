from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class WriteOffToProductionUnitCreate(BaseModel):
    object_unit_id: Annotated[UUID, Field(ge=1, description="Идентификатор единицы объекта")]


class WriteOffToProductionCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255, description="Название операции списания в производство")]
    order_id: Annotated[int, Field(ge=1, description="Идентификатор производственного заказа")]
    units: list[WriteOffToProductionUnitCreate]
