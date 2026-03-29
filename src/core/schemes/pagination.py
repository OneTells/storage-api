from typing import Annotated

from pydantic import BaseModel, Field


class Pagination(BaseModel):
    page: Annotated[int, Field(ge=1, description="Текущая страница")]
    limit: Annotated[int, Field(ge=1, le=1000, description="Количество элементов на странице")]
    total: Annotated[int, Field(ge=0, description="Общее количество элементов")]
    pages: Annotated[int, Field(ge=0, description="Общее количество страниц")]
    has_next: Annotated[bool, Field(description="Есть следующая страница")]
    has_prev: Annotated[bool, Field(description="Есть предыдущая страница")]
