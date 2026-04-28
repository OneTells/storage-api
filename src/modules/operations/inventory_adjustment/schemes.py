from typing import Annotated
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, Field

from core.models import ObjectUnitStatus


class InventoryAdjustmentUnitCreate(BaseModel):
    object_unit_id: Annotated[UUID, Field(ge=1, description="Идентификатор единицы объекта")]
    warehouse_id: Annotated[int | None, Field(ge=1, description="Идентификатор склада")]
    status: Annotated[ObjectUnitStatus, Field(description="Статус единицы объекта")]
    reason: Annotated[str | None, Field(max_length=500, description="Причина корректировки")] = None


class InventoryAdjustmentCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255, description="Название операции инвентаризации")]
    inventory_date: Annotated[AwareDatetime, Field(description="Дата инвентаризации")]
    reason: Annotated[str | None, Field(max_length=500, description="Причина корректировки")] = None
    units: list[InventoryAdjustmentUnitCreate]
