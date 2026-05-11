from typing import Annotated

from pydantic import BaseModel, Field

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
    id: IdField
