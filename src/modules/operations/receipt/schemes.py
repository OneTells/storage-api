from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field


class ReceiptUnitCreate(BaseModel):
    object_id: Annotated[int, Field(ge=1, description="Идентификатор объекта")]
    warehouse_id: Annotated[int, Field(ge=1, description="Идентификатор склада")]
    price: Annotated[Decimal | None, Field(ge=0, decimal_places=2, description="Цена")] = None


class ReceiptCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255, description="Название операции")]
    supplier_id: Annotated[int, Field(ge=1, description="Идентификатор клиента")]
    units: list[ReceiptUnitCreate]
