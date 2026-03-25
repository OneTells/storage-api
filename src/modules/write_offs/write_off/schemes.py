from typing import Annotated

from pydantic import BaseModel, Field


class WriteOffItemModel(BaseModel):
    object_id: Annotated[int, Field(gt=0)]

    warehouse_id: Annotated[int, Field(gt=0)]
    reason: Annotated[str, Field(min_length=1)]
