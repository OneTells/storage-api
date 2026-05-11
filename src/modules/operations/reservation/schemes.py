from decimal import Decimal
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field

from core.models import ReservationStatus
from core.schemes import Pagination

IdField = Annotated[int, Field(ge=1, description="Идентификатор операции (stock_operations.id)")]


class ReservationItemCreate(BaseModel):
    material_id: Annotated[int, Field(ge=1, description="Идентификатор материала")]
    quantity: Annotated[Decimal, Field(gt=0, decimal_places=3, description="Резервируемое количество")]


class ReservationCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255, description="Наименование операции")]
    warehouse_id: Annotated[int, Field(ge=1, description="Склад, с которого резервируется остаток (FIFO по партиям)")]
    items: Annotated[
        list[ReservationItemCreate],
        Field(
            min_length=1,
            max_length=1,
            description="Одна позиция резерва (материал и количество); партия подбирается автоматически по FIFO",
        ),
    ]


class ReservationUpdate(BaseModel):
    name: Annotated[str | None, Field(default=None, min_length=1, max_length=255)] = None
    performed_at: AwareDatetime | None = None
    quantity: Annotated[Decimal | None, Field(default=None, gt=0, decimal_places=3)] = None
    status: ReservationStatus | None = None


class ReservationCancelRequest(BaseModel):
    operation_id: IdField


class ReservationRead(BaseModel):
    id: Annotated[int, Field(ge=1, description="Идентификатор операции")]
    name: Annotated[str, Field(description="Наименование операции")]
    performed_at: AwareDatetime
    status: Annotated[ReservationStatus, Field(description="Статус резерва")]
    batch_id: Annotated[int, Field(ge=1)]
    quantity: Annotated[Decimal, Field(gt=0, decimal_places=3)]
    created_by_id: Annotated[int, Field(ge=1)]
    created_at: AwareDatetime
    completed_at: AwareDatetime | None
    cancelled_at: AwareDatetime | None


class ReservationsListResponse(BaseModel):
    items: list[ReservationRead]
    pagination: Pagination
