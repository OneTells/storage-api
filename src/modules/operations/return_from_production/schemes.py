from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class ReturnFromProductionUnitCreate(BaseModel):
    object_unit_id: Annotated[UUID, Field(ge=1, description="Идентификатор единицы объекта")]
    warehouse_id: Annotated[int, Field(ge=1, description="Идентификатор склада")]
    reason: Annotated[str | None, Field(max_length=500, description="Причина возврата")] = None


class ReturnFromProductionCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255, description="Название операции возврата из производства")]
    order_id: Annotated[int, Field(ge=1, description="Идентификатор производственного заказа")]
    reason: Annotated[str | None, Field(max_length=500, description="Причина возврата")] = None
    units: list[ReturnFromProductionUnitCreate]
