from decimal import Decimal
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field

from core.models import ProductionOrderStatus
from core.schemes import Pagination


class NamedEntityRef(BaseModel):
    """Ссылка на сущность с человекочитаемым именем (без «голого» id)."""

    id: Annotated[int, Field(ge=1, description="Идентификатор")]
    name: Annotated[str, Field(description="Наименование")]


class MaterialEntityRef(BaseModel):
    id: Annotated[int, Field(ge=1)]
    name: Annotated[str, Field(description="Наименование материала")]
    sku: Annotated[str, Field(description="Артикул / SKU")]


class ProductionOrderProductLineRead(BaseModel):
    id: Annotated[int, Field(ge=1, description="Идентификатор строки заказа")]
    product: Annotated[NamedEntityRef, Field(description="Продукт")]
    quantity: Annotated[Decimal, Field(gt=0, decimal_places=3, description="Количество")]


class ProductionOrderResourceLineRead(BaseModel):
    id: Annotated[int, Field(ge=1)]
    resource: Annotated[NamedEntityRef, Field(description="Ресурс")]
    quantity: Annotated[Decimal, Field(gt=0, decimal_places=3)]


class ProductionOrderWorkerLineRead(BaseModel):
    id: Annotated[int, Field(ge=1)]
    employee: Annotated[NamedEntityRef, Field(description="Сотрудник (полное имя в name)")]
    hours_worked: Annotated[Decimal, Field(ge=0, decimal_places=2)]
    hourly_rate: Annotated[Decimal, Field(ge=0, decimal_places=2)]


class MaterialReservationRead(BaseModel):
    """Материал заказа: план и накопленный резерв (по данным production_order_materials)."""

    material: Annotated[MaterialEntityRef, Field(description="Материал")]
    reserved_quantity: Annotated[Decimal, Field(ge=0, decimal_places=3, description="Зарезервировано")]
    planned_quantity: Annotated[Decimal, Field(ge=0, decimal_places=3, description="Плановое количество")]


class ProductionOrderRead(BaseModel):
    id: Annotated[int, Field(ge=1)]
    performed_at: AwareDatetime
    delivery_warehouse: Annotated[NamedEntityRef, Field(description="Склад приёмки / выдачи по заказу")]
    write_off_warehouses: Annotated[
        list[NamedEntityRef],
        Field(default_factory=list, description="Склады списания материалов в производство"),
    ]
    comment: Annotated[str, Field(description="Комментарий")]
    status: ProductionOrderStatus
    created_by: Annotated[NamedEntityRef, Field(description="Создатель заказа")]
    created_at: AwareDatetime
    completed_at: AwareDatetime | None
    closed_at: AwareDatetime | None
    cancelled_at: AwareDatetime | None
    products: Annotated[list[ProductionOrderProductLineRead], Field(default_factory=list)]
    resources: Annotated[list[ProductionOrderResourceLineRead], Field(default_factory=list)]
    workers: Annotated[list[ProductionOrderWorkerLineRead], Field(default_factory=list)]
    material_reservations: Annotated[list[MaterialReservationRead], Field(default_factory=list)]


class ProductionOrdersListResponse(BaseModel):
    production_orders: list[ProductionOrderRead]
    pagination: Pagination
