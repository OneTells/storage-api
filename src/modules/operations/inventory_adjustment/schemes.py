from decimal import Decimal
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field

from core.models import OperationStatus
from core.schemes import Pagination
from modules.operations.schemes import OperationUserRef


class InventoryAdjustmentItemCreate(BaseModel):
    material_id: Annotated[int, Field(ge=1, description="Идентификатор материала")]
    expected_qty: Annotated[Decimal, Field(ge=0, decimal_places=3, description="Учётное количество")]
    actual_qty: Annotated[Decimal, Field(ge=0, decimal_places=3, description="Фактическое количество")]


class InventoryAdjustmentCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255, description="Наименование операции")]
    performed_at: Annotated[AwareDatetime, Field(description="Дата проведения инвентаризации")]
    warehouse_id: Annotated[int, Field(ge=1, description="Идентификатор склада")]
    description: Annotated[str, Field(min_length=1, description="Комментарий / описание инвентаризации")]
    status: Annotated[
        OperationStatus,
        Field(default=OperationStatus.DRAFT, description="Статус инвентаризации при создании"),
    ] = OperationStatus.DRAFT
    items: list[InventoryAdjustmentItemCreate]


class InventoryAdjustmentUpdate(BaseModel):
    name: Annotated[str | None, Field(default=None, min_length=1, max_length=255)] = None
    performed_at: AwareDatetime | None = None
    warehouse_id: Annotated[int | None, Field(default=None, ge=1)] = None
    description: Annotated[str | None, Field(default=None, min_length=1)] = None
    status: OperationStatus | None = None
    items: list[InventoryAdjustmentItemCreate] | None = None


class InventoryAdjustmentItemRead(BaseModel):
    """Строка инвентаризации в ответе (как при создании)."""

    material_id: Annotated[int, Field(ge=1, description="Идентификатор материала")]
    expected_qty: Annotated[Decimal, Field(ge=0, decimal_places=3, description="Учётное количество")]
    actual_qty: Annotated[Decimal, Field(ge=0, decimal_places=3, description="Фактическое количество")]


class InventoryAdjustmentRead(BaseModel):
    id: Annotated[int, Field(ge=1, description="Идентификатор операции")]
    name: Annotated[str, Field(description="Наименование операции")]
    performed_at: AwareDatetime
    status: Annotated[OperationStatus, Field(description="Статус инвентаризации")]
    warehouse_id: Annotated[int, Field(ge=1)]
    description: Annotated[str, Field(description="Описание операции")]
    created_by: Annotated[OperationUserRef, Field(description="Пользователь, создавший операцию")]
    created_at: AwareDatetime
    completed_at: AwareDatetime | None
    cancelled_at: AwareDatetime | None
    items: Annotated[
        list[InventoryAdjustmentItemRead],
        Field(default_factory=list, description="Строки инвентаризации"),
    ]


class InventoryAdjustmentsListResponse(BaseModel):
    items: list[InventoryAdjustmentRead]
    pagination: Pagination
