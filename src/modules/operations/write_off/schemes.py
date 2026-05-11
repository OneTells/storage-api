from decimal import Decimal
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field

from core.models import OperationStatus
from core.schemes import Pagination
from modules.operations.schemes import OperationUserRef


class WriteOffItemCreate(BaseModel):
    material_id: Annotated[int, Field(ge=1, description="Идентификатор материала")]
    quantity: Annotated[Decimal, Field(gt=0, decimal_places=3, description="Количество")]
    reason: Annotated[str, Field(min_length=1, description="Причина списания по строке")]


class WriteOffCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255, description="Наименование операции")]
    performed_at: Annotated[AwareDatetime, Field(description="Дата проведения операции")]
    warehouse_id: Annotated[int, Field(ge=1, description="Идентификатор склада")]
    reason: Annotated[str, Field(min_length=1, description="Общая причина списания (шапка операции)")]
    items: list[WriteOffItemCreate]


class WriteOffUpdate(BaseModel):
    name: Annotated[str | None, Field(default=None, min_length=1, max_length=255)] = None
    performed_at: AwareDatetime | None = None
    warehouse_id: Annotated[int | None, Field(default=None, ge=1)] = None
    reason: Annotated[str | None, Field(default=None, min_length=1)] = None
    status: OperationStatus | None = None
    items: list[WriteOffItemCreate] | None = None


class WriteOffItemRead(BaseModel):
    """Строка списания в ответе (как при создании, плюс партия при наличии)."""

    material_id: Annotated[int, Field(ge=1, description="Идентификатор материала")]
    quantity: Annotated[Decimal, Field(gt=0, decimal_places=3, description="Количество")]
    reason: Annotated[str, Field(min_length=1, description="Причина списания по строке")]
    batch_id: Annotated[int | None, Field(description="Идентификатор партии списания")] = None


class WriteOffRead(BaseModel):
    id: Annotated[int, Field(ge=1, description="Идентификатор операции")]
    name: Annotated[str, Field(description="Наименование операции")]
    performed_at: AwareDatetime
    status: Annotated[OperationStatus, Field(description="Статус списания")]
    warehouse_id: Annotated[int, Field(ge=1)]
    reason: Annotated[str, Field(description="Общая причина списания")]
    created_by: Annotated[OperationUserRef, Field(description="Пользователь, создавший операцию")]
    created_at: AwareDatetime
    completed_at: AwareDatetime | None
    cancelled_at: AwareDatetime | None
    items: Annotated[
        list[WriteOffItemRead],
        Field(default_factory=list, description="Строки списания"),
    ]


class WriteOffsListResponse(BaseModel):
    items: list[WriteOffRead]
    pagination: Pagination
