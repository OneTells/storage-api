from decimal import Decimal
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field

from core.models import OperationStatus
from core.schemes import Pagination


class ProductionOutputItemCreate(BaseModel):
    material_id: Annotated[int, Field(ge=1, description="Идентификатор материала")]
    quantity: Annotated[Decimal, Field(gt=0, decimal_places=3, description="Количество")]
    unit_price: Annotated[Decimal, Field(ge=0, decimal_places=2, description="Цена выпуска за единицу")]


class ProductionOutputCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255, description="Наименование операции")]
    performed_at: Annotated[AwareDatetime, Field(description="Дата проведения операции")]
    production_order_id: Annotated[int, Field(ge=1, description="Идентификатор производственного заказа")]
    warehouse_id: Annotated[int, Field(ge=1, description="Идентификатор склада оприходования")]
    items: list[ProductionOutputItemCreate]


class ProductionOutputUpdate(BaseModel):
    name: Annotated[str | None, Field(default=None, min_length=1, max_length=255)] = None
    performed_at: AwareDatetime | None = None
    production_order_id: Annotated[int | None, Field(default=None, ge=1)] = None
    warehouse_id: Annotated[int | None, Field(default=None, ge=1)] = None
    status: OperationStatus | None = None
    items: list[ProductionOutputItemCreate] | None = None


class ProductionOutputRead(BaseModel):
    id: Annotated[int, Field(ge=1, description="Идентификатор операции")]
    name: Annotated[str, Field(description="Наименование операции")]
    performed_at: AwareDatetime
    status: Annotated[OperationStatus, Field(description="Статус выпуска")]
    production_order_id: Annotated[int, Field(ge=1)]
    warehouse_id: Annotated[int, Field(ge=1)]
    created_by_id: Annotated[int, Field(ge=1)]
    created_at: AwareDatetime
    completed_at: AwareDatetime | None
    cancelled_at: AwareDatetime | None


class ProductionOutputsListResponse(BaseModel):
    items: list[ProductionOutputRead]
    pagination: Pagination
