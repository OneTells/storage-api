from decimal import Decimal
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field

from core.models import ProductionOrderStatus


class ProductionOrderProductLineWrite(BaseModel):
    product_id: Annotated[int, Field(ge=1)]
    quantity: Annotated[Decimal, Field(gt=0, decimal_places=3)]


class ProductionOrderResourceLineWrite(BaseModel):
    resource_id: Annotated[int, Field(ge=1)]
    quantity: Annotated[Decimal, Field(gt=0, decimal_places=3)]


class ProductionOrderWorkerLineWrite(BaseModel):
    employee_id: Annotated[int, Field(ge=1)]
    hours_worked: Annotated[Decimal, Field(ge=0, decimal_places=2)]
    hourly_rate: Annotated[Decimal, Field(ge=0, decimal_places=2)]


class ProductionOrderCreate(BaseModel):
    performed_at: AwareDatetime
    warehouse_ids: Annotated[
        list[Annotated[int, Field(ge=1)]],
        Field(default_factory=list, description="Склады, с которых допускается списание (junction)"),
    ]
    delivery_warehouse_id: Annotated[int, Field(ge=1, description="Склад оприходования выпуска")]
    products: list[ProductionOrderProductLineWrite]
    resources: list[ProductionOrderResourceLineWrite]
    workers: list[ProductionOrderWorkerLineWrite]


class ProductionOrderCreateResponse(BaseModel):
    id: Annotated[int, Field(ge=1)]


class ProductionOrderPatch(BaseModel):
    performed_at: AwareDatetime | None = None
    warehouse_ids: list[Annotated[int, Field(ge=1)]] | None = None
    delivery_warehouse_id: Annotated[int | None, Field(default=None, ge=1)] = None
    comment: str | None = None
    status: ProductionOrderStatus | None = None
    products: list[ProductionOrderProductLineWrite] | None = None
    resources: list[ProductionOrderResourceLineWrite] | None = None
    workers: list[ProductionOrderWorkerLineWrite] | None = None


class MaterialReservationAdd(BaseModel):
    material_id: Annotated[int, Field(ge=1)]
    quantity: Annotated[Decimal, Field(gt=0, decimal_places=3, description="Добавляемое к резерву")]


class MaterialReservationCancel(BaseModel):
    material_id: Annotated[int, Field(ge=1)]
    quantity: Annotated[Decimal, Field(gt=0, decimal_places=3, description="Снимаемое с резерва")]
