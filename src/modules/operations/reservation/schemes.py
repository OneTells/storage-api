from typing import Annotated

from pydantic import BaseModel, Field


class ReservationUnitCreate(BaseModel):
    object_unit_id: Annotated[int, Field(ge=1, description="Идентификатор единицы объекта")]


class ReservationCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255, description="Название операции бронирования")]
    order_id: Annotated[int, Field(ge=1, description="Идентификатор заказа")]
    units: list[ReservationUnitCreate]
