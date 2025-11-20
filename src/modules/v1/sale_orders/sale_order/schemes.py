from typing import Annotated

from pydantic import BaseModel, Field


class SaleOrderItemModel(BaseModel):
    object_id: Annotated[int, Field(gt=0)]

    warehouse_id: Annotated[int, Field(gt=0)]
    sale_price: Annotated[float, Field(gt=0)]
