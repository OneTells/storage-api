from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field


class ShipmentUnitCreate(BaseModel):
    object_unit_id: Annotated[int, Field(ge=1, description="Идентификатор единицы объекта")]
    sale_price: Annotated[Decimal, Field(ge=0, decimal_places=2, description="Цена продажи")]


class ShipmentCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255, description="Название операции отгрузки")]
    customer_id: Annotated[int, Field(ge=1, description="Идентификатор клиента")]
    units: list[ShipmentUnitCreate]
