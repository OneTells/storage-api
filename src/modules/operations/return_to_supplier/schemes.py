from typing import Annotated

from pydantic import BaseModel, Field


class ReturnToSupplierUnitCreate(BaseModel):
    object_unit_id: Annotated[int, Field(ge=1, description="Идентификатор единицы объекта")]
    reason: Annotated[str | None, Field(max_length=500, description="Причина возврата")] = None


class ReturnToSupplierCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255, description="Название операции возврата поставщику")]
    supplier_id: Annotated[int, Field(ge=1, description="Идентификатор поставщика")]
    reason: Annotated[str | None, Field(max_length=500, description="Причина возврата")] = None
    units: list[ReturnToSupplierUnitCreate]
