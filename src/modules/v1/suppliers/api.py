from typing import Annotated

from asyncpg import Connection
from fastapi import APIRouter, Depends

from core.methods import get_connection
from .supplier.api import router as supplier_router

router = APIRouter(prefix="/suppliers")
router.include_router(supplier_router)


@router.get('/')
async def get_suppliers(
    connection: Annotated[Connection, Depends(get_connection)]
):
    ...
