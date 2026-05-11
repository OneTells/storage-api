from decimal import Decimal
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field

from core.models import OperationStatus
from core.schemes import Pagination
from modules.operations.schemes import OperationProductionOrderRef, OperationUserRef


class ProductionOutputItemCreate(BaseModel):
    material_id: Annotated[int, Field(ge=1, description="Идентификатор материала")]
    quantity: Annotated[Decimal, Field(gt=0, decimal_places=3, description="Количество")]
    unit_price: Annotated[Decimal, Field(ge=0, decimal_places=2, description="Цена выпуска за единицу")]


class ProductionOutputCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255, description="Наименование операции")]
    performed_at: Annotated[AwareDatetime, Field(description="Дата проведения операции")]
    production_order_id: Annotated[int, Field(ge=1, description="Идентификатор производственного заказа")]
    warehouse_id: Annotated[int, Field(ge=1, description="Идентификатор склада оприходования")]
    status: Annotated[
        OperationStatus,
        Field(default=OperationStatus.DRAFT, description="Статус выпуска при создании"),
    ] = OperationStatus.DRAFT
    items: list[ProductionOutputItemCreate]


class ProductionOutputUpdate(BaseModel):
    name: Annotated[str | None, Field(default=None, min_length=1, max_length=255)] = None
    performed_at: AwareDatetime | None = None
    production_order_id: Annotated[int | None, Field(default=None, ge=1)] = None
    warehouse_id: Annotated[int | None, Field(default=None, ge=1)] = None
    status: OperationStatus | None = None
    items: list[ProductionOutputItemCreate] | None = None


class ProductionOutputItemRead(BaseModel):
    """Позиция выпуска в ответе (как при создании, плюс партия при наличии)."""

    material_id: Annotated[int, Field(ge=1, description="Идентификатор материала")]
    quantity: Annotated[Decimal, Field(gt=0, decimal_places=3, description="Количество")]
    unit_price: Annotated[Decimal, Field(ge=0, decimal_places=2, description="Цена выпуска за единицу")]
    batch_id: Annotated[int | None, Field(description="Идентификатор созданной партии")] = None


class ProductionOutputRead(BaseModel):
    id: Annotated[int, Field(ge=1, description="Идентификатор операции")]
    name: Annotated[str, Field(description="Наименование операции")]
    performed_at: AwareDatetime
    status: Annotated[OperationStatus, Field(description="Статус выпуска")]
    production_order: Annotated[
        OperationProductionOrderRef,
        Field(description="Производственный заказ"),
    ]
    warehouse_id: Annotated[int, Field(ge=1)]
    created_by: Annotated[OperationUserRef, Field(description="Пользователь, создавший операцию")]
    created_at: AwareDatetime
    completed_at: AwareDatetime | None
    cancelled_at: AwareDatetime | None
    items: Annotated[
        list[ProductionOutputItemRead],
        Field(default_factory=list, description="Позиции выпуска"),
    ]


class ProductionOutputsListResponse(BaseModel):
    items: list[ProductionOutputRead]
    pagination: Pagination
