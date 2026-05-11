from typing import Annotated

from pydantic import BaseModel, Field

from core.models import OperationStatus, ReceiptStatus, ReservationStatus

IdField = Annotated[int, Field(ge=1, description="Идентификатор операции (stock_operations.id)")]


class OperationUserRef(BaseModel):
    """Пользователь, создавший операцию (идентификатор и человекочитаемое имя)."""

    id: Annotated[int, Field(ge=1, description="Идентификатор пользователя")]
    name: Annotated[str, Field(description="Имя пользователя")]


class OperationCounterpartyRef(BaseModel):
    """Контрагент (поставщик, клиент и т.п.): идентификатор и наименование."""

    id: Annotated[int, Field(ge=1, description="Идентификатор контрагента")]
    name: Annotated[str, Field(description="Наименование контрагента")]


class OperationProductionOrderRef(BaseModel):
    """Производственный заказ в ответе API: идентификатор и текстовое поле (комментарий)."""

    id: Annotated[int, Field(ge=1, description="Идентификатор производственного заказа")]
    comment: Annotated[str, Field(description="Комментарий к заказу")]


class OperationCreateResponse(BaseModel):
    """Ответ POST при создании складской операции: идентификатор и начальный статус (тип enum зависит от вида операции)."""

    id: IdField
    status: Annotated[
        OperationStatus | ReceiptStatus | ReservationStatus,
        Field(description="Статус операции сразу после создания"),
    ]
