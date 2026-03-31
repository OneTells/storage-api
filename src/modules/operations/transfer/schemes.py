from typing import Annotated

from pydantic import BaseModel, Field


class TransferUnitCreate(BaseModel):
    object_unit_id: Annotated[int, Field(ge=1, description="Идентификатор единицы объекта")]
    warehouse_id: Annotated[int, Field(ge=1, description="Идентификатор целевого склада")]


class TransferCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255, description="Название операции перемещения")]
    comment: Annotated[str | None, Field(max_length=500, description="Комментарий к перемещению")] = None
    units: list[TransferUnitCreate]
