from typing import Annotated

from fastapi import Path

ObjectIdType = Annotated[int, Path(ge=1, description="Идентификатор объекта")]
