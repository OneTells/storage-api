from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field


class ProductionOutputUnitCreate(BaseModel):
    object_id: Annotated[int, Field(ge=1, description="Идентификатор объекта")]
    warehouse_id: Annotated[int, Field(ge=1, description="Идентификатор склада")]
    cost_price: Annotated[Decimal | None, Field(ge=0, decimal_places=2, description="Себестоимость")] = None


class ProductionOutputCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255, description="Название операции выпуска продукции")]
    order_id: Annotated[int, Field(ge=1, description="Идентификатор производственного заказа")]
    units: list[ProductionOutputUnitCreate]
