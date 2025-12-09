from typing import Annotated

from pydantic import BaseModel, Field


class TransferItemModel(BaseModel):
    object_id: Annotated[int, Field(gt=0)]

    source_warehouse_id: Annotated[int, Field(gt=0)]
    destination_warehouse_id: Annotated[int, Field(gt=0)]
