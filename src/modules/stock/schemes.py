from typing import Annotated

from pydantic import BaseModel, Field

from core.schemes import Pagination


class StockItemRead(BaseModel):
    object_id: Annotated[int, Field(ge=1, description="Идентификатор объекта")]
    warehouse_id: Annotated[int, Field(ge=1, description="Идентификатор склада")]
    quantity: Annotated[int, Field(ge=0, description="Количество единиц")]


class StockReadResponse(BaseModel):
    stocks: Annotated[list[StockItemRead], Field(description="Агрегированные остатки")]
    pagination: Annotated[Pagination, Field(description="Информация о пагинации")]
