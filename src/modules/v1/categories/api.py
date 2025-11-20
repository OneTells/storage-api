from typing import Annotated

from asyncpg import Connection
from fastapi import APIRouter, Depends

from core.methods import get_connection
from .category.api import router as category_router

router = APIRouter(prefix="/categories")
router.include_router(category_router)


@router.get('/')
async def get_categories(
    connection: Annotated[Connection, Depends(get_connection)]
):
    ...
