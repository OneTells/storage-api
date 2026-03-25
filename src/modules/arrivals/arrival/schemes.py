from typing import Annotated

from pydantic import BaseModel, Field, AwareDatetime

from core.models.arrivals import ArrivalStatus


class ArrivalItemModel(BaseModel):
    object_id: Annotated[int, Field(gt=0)]
    warehouse_id: Annotated[int, Field(gt=0)]
    price: Annotated[float, Field(gt=0)]


class ArrivalItemWithIdModel(ArrivalItemModel):
    id: Annotated[int, Field(gt=0)]
    object_unit_id: Annotated[int | None, Field(gt=0)]


class ArrivalModel(BaseModel):
    id: Annotated[int, Field(gt=0)]

    supplier_id: Annotated[int, Field(gt=0)]

    name: Annotated[str, Field(min_length=1)]
    status: Annotated[ArrivalStatus, Field()]

    items: list[ArrivalItemWithIdModel]

    created_at: AwareDatetime
