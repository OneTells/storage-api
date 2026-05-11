from decimal import Decimal
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field

from core.models import OperationStatus
from core.schemes import Pagination


class ShipmentItemCreate(BaseModel):
    material_id: Annotated[int, Field(ge=1, description="Идентификатор материала")]
    quantity: Annotated[Decimal, Field(gt=0, decimal_places=3, description="Количество")]


class ShipmentCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255, description="Наименование операции")]
    performed_at: Annotated[AwareDatetime, Field(description="Дата проведения операции")]
    warehouse_id: Annotated[int, Field(ge=1, description="Идентификатор склада")]
    customer_id: Annotated[int, Field(ge=1, description="Идентификатор клиента")]
    order_number: Annotated[str | None, Field(max_length=100, description="Номер заказа клиента")] = None
    items: list[ShipmentItemCreate]


class ShipmentUpdate(BaseModel):
    name: Annotated[str | None, Field(default=None, min_length=1, max_length=255)] = None
    performed_at: AwareDatetime | None = None
    warehouse_id: Annotated[int | None, Field(default=None, ge=1)] = None
    customer_id: Annotated[int | None, Field(default=None, ge=1)] = None
    order_number: Annotated[str | None, Field(default=None, max_length=100)] = None
    status: OperationStatus | None = None
    items: list[ShipmentItemCreate] | None = None


class ShipmentRead(BaseModel):
    id: Annotated[int, Field(ge=1, description="Идентификатор операции")]
    name: Annotated[str, Field(description="Наименование операции")]
    performed_at: AwareDatetime
    status: Annotated[OperationStatus, Field(description="Статус отгрузки")]
    counterparty_id: Annotated[int, Field(ge=1, description="Идентификатор клиента")]
    warehouse_id: Annotated[int, Field(ge=1, description="Идентификатор склада")]
    order_number: Annotated[str | None, Field(max_length=100)]
    created_by_id: Annotated[int, Field(ge=1)]
    created_at: AwareDatetime
    completed_at: AwareDatetime | None
    cancelled_at: AwareDatetime | None


class ShipmentsListResponse(BaseModel):
    items: list[ShipmentRead]
    pagination: Pagination
