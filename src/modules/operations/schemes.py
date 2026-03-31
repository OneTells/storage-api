from typing import Annotated

from pydantic import BaseModel, Field

IdField = Annotated[int, Field(ge=1, description="Идентификатор операции")]


class OperationCreateResponse(BaseModel):
    id: IdField
