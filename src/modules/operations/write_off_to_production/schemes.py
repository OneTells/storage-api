from decimal import Decimal
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field

from core.models import OperationStatus
from core.schemes import Pagination
from modules.operations.schemes import OperationUserRef


class WriteOffToProductionItemCreate(BaseModel):
    material_id: Annotated[int, Field(ge=1, description="Идентификатор материала")]
    quantity: Annotated[Decimal, Field(gt=0, decimal_places=3, description="Количество")]
    unit_price: Annotated[Decimal, Field(ge=0, decimal_places=2, description="Цена списания за единицу")]


class WriteOffToProductionCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255, description="Наименование операции")]
    performed_at: Annotated[AwareDatetime, Field(description="Дата проведения операции")]
    warehouse_id: Annotated[int, Field(ge=1, description="Идентификатор склада списания")]
    production_order_reference: Annotated[
        str | None,
        Field(max_length=100, description="Номер или текстовый идентификатор производственного заказа (как в БД)"),
    ] = None
    items: list[WriteOffToProductionItemCreate]


class WriteOffToProductionUpdate(BaseModel):
    name: Annotated[str | None, Field(default=None, min_length=1, max_length=255)] = None
    performed_at: AwareDatetime | None = None
    warehouse_id: Annotated[int | None, Field(default=None, ge=1)] = None
    production_order_reference: Annotated[str | None, Field(default=None, max_length=100)] = None
    status: OperationStatus | None = None
    items: list[WriteOffToProductionItemCreate] | None = None


class WriteOffToProductionItemRead(BaseModel):
    """Строка списания в производство в ответе (как при создании, плюс партия при наличии)."""

    material_id: Annotated[int, Field(ge=1, description="Идентификатор материала")]
    quantity: Annotated[Decimal, Field(gt=0, decimal_places=3, description="Количество")]
    unit_price: Annotated[Decimal, Field(ge=0, decimal_places=2, description="Цена списания за единицу")]
    batch_id: Annotated[int | None, Field(description="Идентификатор партии списания")] = None


class WriteOffToProductionRead(BaseModel):
    id: Annotated[int, Field(ge=1, description="Идентификатор операции")]
    name: Annotated[str, Field(description="Наименование операции")]
    performed_at: AwareDatetime
    status: Annotated[OperationStatus, Field(description="Статус списания в производство")]
    warehouse_id: Annotated[int, Field(ge=1)]
    production_order_reference: Annotated[str | None, Field(max_length=100)]
    created_by: Annotated[OperationUserRef, Field(description="Пользователь, создавший операцию")]
    created_at: AwareDatetime
    completed_at: AwareDatetime | None
    cancelled_at: AwareDatetime | None
    items: Annotated[
        list[WriteOffToProductionItemRead],
        Field(default_factory=list, description="Позиции списания в производство"),
    ]


class WriteOffsToProductionListResponse(BaseModel):
    items: list[WriteOffToProductionRead]
    pagination: Pagination
