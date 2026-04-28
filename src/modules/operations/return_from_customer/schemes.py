from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class ReturnFromCustomerUnitCreate(BaseModel):
    object_unit_id: Annotated[UUID, Field(ge=1, description="Идентификатор единицы объекта")]
    warehouse_id: Annotated[int, Field(ge=1, description="Идентификатор склада")]
    is_defective: Annotated[bool, Field(description="Флаг, указывающий на то, что товар в порядке")]
    reason: Annotated[str | None, Field(max_length=500, description="Причина возврата")] = None
    condition: Annotated[str | None, Field(max_length=255, description="Состояние товара")] = None


class ReturnFromCustomerCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255, description="Название операции возврата от клиента")]
    customer_id: Annotated[int, Field(ge=1, description="Идентификатор клиента")]
    reason: Annotated[str | None, Field(max_length=500, description="Причина возврата")] = None
    units: list[ReturnFromCustomerUnitCreate]
