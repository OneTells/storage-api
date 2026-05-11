from decimal import Decimal
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field

from core.models import OperationStatus
from core.schemes import Pagination


class TransferItemCreate(BaseModel):
    material_id: Annotated[int, Field(ge=1, description="Идентификатор материала")]
    quantity: Annotated[Decimal, Field(gt=0, decimal_places=3, description="Количество")]


class TransferCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255, description="Наименование операции")]
    performed_at: Annotated[AwareDatetime, Field(description="Дата проведения операции")]
    from_warehouse_id: Annotated[int, Field(ge=1, description="Склад-отправитель")]
    to_warehouse_id: Annotated[int, Field(ge=1, description="Склад-получатель")]
    items: list[TransferItemCreate]


class TransferUpdate(BaseModel):
    name: Annotated[str | None, Field(default=None, min_length=1, max_length=255)] = None
    performed_at: AwareDatetime | None = None
    from_warehouse_id: Annotated[int | None, Field(default=None, ge=1)] = None
    to_warehouse_id: Annotated[int | None, Field(default=None, ge=1)] = None
    status: OperationStatus | None = None
    items: list[TransferItemCreate] | None = None


class TransferRead(BaseModel):
    id: Annotated[int, Field(ge=1, description="Идентификатор операции")]
    name: Annotated[str, Field(description="Наименование операции")]
    performed_at: AwareDatetime
    status: Annotated[OperationStatus, Field(description="Статус перемещения")]
    from_warehouse_id: Annotated[int, Field(ge=1)]
    to_warehouse_id: Annotated[int, Field(ge=1)]
    created_by_id: Annotated[int, Field(ge=1)]
    created_at: AwareDatetime
    completed_at: AwareDatetime | None
    cancelled_at: AwareDatetime | None


class TransfersListResponse(BaseModel):
    items: list[TransferRead]
    pagination: Pagination
