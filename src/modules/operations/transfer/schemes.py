from decimal import Decimal
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field

from core.models import OperationStatus
from core.schemes import Pagination
from modules.operations.schemes import OperationUserRef


class TransferItemCreate(BaseModel):
    material_id: Annotated[int, Field(ge=1, description="Идентификатор материала")]
    quantity: Annotated[Decimal, Field(gt=0, decimal_places=3, description="Количество")]


class TransferCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255, description="Наименование операции")]
    performed_at: Annotated[AwareDatetime, Field(description="Дата проведения операции")]
    from_warehouse_id: Annotated[int, Field(ge=1, description="Склад-отправитель")]
    to_warehouse_id: Annotated[int, Field(ge=1, description="Склад-получатель")]
    status: Annotated[
        OperationStatus,
        Field(default=OperationStatus.DRAFT, description="Статус перемещения при создании"),
    ] = OperationStatus.DRAFT
    items: list[TransferItemCreate]


class TransferUpdate(BaseModel):
    name: Annotated[str | None, Field(default=None, min_length=1, max_length=255)] = None
    performed_at: AwareDatetime | None = None
    from_warehouse_id: Annotated[int | None, Field(default=None, ge=1)] = None
    to_warehouse_id: Annotated[int | None, Field(default=None, ge=1)] = None
    status: OperationStatus | None = None
    items: list[TransferItemCreate] | None = None


class TransferItemRead(BaseModel):
    """Строка перемещения в ответе (как при создании, плюс партии после проведения)."""

    material_id: Annotated[int, Field(ge=1, description="Идентификатор материала")]
    quantity: Annotated[Decimal, Field(gt=0, decimal_places=3, description="Количество")]
    old_batch_id: Annotated[int | None, Field(description="Исходная партия")] = None
    new_batch_id: Annotated[int | None, Field(description="Партия на складе получателе")] = None


class TransferRead(BaseModel):
    id: Annotated[int, Field(ge=1, description="Идентификатор операции")]
    name: Annotated[str, Field(description="Наименование операции")]
    performed_at: AwareDatetime
    status: Annotated[OperationStatus, Field(description="Статус перемещения")]
    from_warehouse_id: Annotated[int, Field(ge=1)]
    to_warehouse_id: Annotated[int, Field(ge=1)]
    created_by: Annotated[OperationUserRef, Field(description="Пользователь, создавший операцию")]
    created_at: AwareDatetime
    completed_at: AwareDatetime | None
    cancelled_at: AwareDatetime | None
    items: Annotated[
        list[TransferItemRead],
        Field(default_factory=list, description="Позиции перемещения"),
    ]


class TransfersListResponse(BaseModel):
    items: list[TransferRead]
    pagination: Pagination
