from typing import Annotated

from pydantic import BaseModel, Field

from core.schemes import Pagination
from modules.object_units.object_unit.schemes import ObjectUnitRead


class ObjectUnitsReadResponse(BaseModel):
    object_units: Annotated[list[ObjectUnitRead], Field(description="Список единиц объекта")]
    pagination: Annotated[Pagination, Field(description="Информация о пагинации")]
