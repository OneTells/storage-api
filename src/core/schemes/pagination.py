from pydantic import BaseModel


class Pagination(BaseModel):
    page: int
    limit: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool
