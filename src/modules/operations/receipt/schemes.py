from decimal import Decimal
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field

from core.models import ReceiptStatus
from core.schemes import Pagination
from modules.operations.schemes import OperationCounterpartyRef, OperationUserRef


class ReceiptItemCreate(BaseModel):
    material_id: Annotated[int, Field(ge=1, description="Идентификатор материала")]
    quantity: Annotated[Decimal, Field(gt=0, decimal_places=3, description="Количество")]
    unit_price: Annotated[Decimal, Field(ge=0, decimal_places=2, description="Цена закупки за единицу")]


class ReceiptCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255, description="Наименование операции")]
    performed_at: Annotated[AwareDatetime, Field(description="Дата проведения операции")]
    warehouse_id: Annotated[int, Field(ge=1, description="Идентификатор склада")]
    supplier_id: Annotated[int, Field(ge=1, description="Идентификатор поставщика")]
    shipping_price: Annotated[Decimal, Field(ge=0, decimal_places=2, description="Стоимость доставки")] = Decimal(
        "0"
    )
    discount: Annotated[Decimal, Field(ge=0, decimal_places=2, description="Скидка на приёмку")] = Decimal("0")
    status: Annotated[
        ReceiptStatus,
        Field(default=ReceiptStatus.DRAFT, description="Статус приёмки при создании"),
    ] = ReceiptStatus.DRAFT
    items: list[ReceiptItemCreate]


class ReceiptUpdate(BaseModel):
    name: Annotated[str | None, Field(default=None, min_length=1, max_length=255, description="Наименование операции")] = None
    performed_at: Annotated[AwareDatetime | None, Field(default=None, description="Дата проведения операции")] = None
    warehouse_id: Annotated[int | None, Field(default=None, ge=1, description="Идентификатор склада")] = None
    supplier_id: Annotated[int | None, Field(default=None, ge=1, description="Идентификатор поставщика")] = None
    shipping_price: Annotated[
        Decimal | None, Field(default=None, ge=0, decimal_places=2, description="Стоимость доставки")] = None
    discount: Annotated[Decimal | None, Field(default=None, ge=0, decimal_places=2, description="Скидка на приёмку")] = None
    status: ReceiptStatus | None = None
    items: list[ReceiptItemCreate] | None = None


class ReceiptItemRead(BaseModel):
    """Позиция приёмки в ответе (как при создании, плюс привязанная партия при наличии)."""

    material_id: Annotated[int, Field(ge=1, description="Идентификатор материала")]
    quantity: Annotated[Decimal, Field(gt=0, decimal_places=3, description="Количество")]
    unit_price: Annotated[Decimal, Field(ge=0, decimal_places=2, description="Цена закупки за единицу")]
    batch_id: Annotated[int | None, Field(description="Идентификатор партии после оприходования")] = None


class ReceiptRead(BaseModel):
    id: Annotated[int, Field(ge=1, description="Идентификатор операции")]
    name: Annotated[str, Field(description="Наименование операции")]
    performed_at: AwareDatetime
    status: Annotated[ReceiptStatus, Field(description="Статус приёмки")]
    supplier: Annotated[
        OperationCounterpartyRef,
        Field(description="Поставщик"),
    ]
    warehouse_id: Annotated[int, Field(ge=1, description="Идентификатор склада")]
    shipping_price: Annotated[Decimal, Field(ge=0, decimal_places=2)]
    discount: Annotated[Decimal, Field(ge=0, decimal_places=2)]
    created_by: Annotated[OperationUserRef, Field(description="Пользователь, создавший операцию")]
    created_at: AwareDatetime
    completed_at: AwareDatetime | None
    cancelled_at: AwareDatetime | None
    items: Annotated[
        list[ReceiptItemRead],
        Field(default_factory=list, description="Позиции приёмки"),
    ]


class ReceiptsListResponse(BaseModel):
    items: list[ReceiptRead]
    pagination: Pagination
