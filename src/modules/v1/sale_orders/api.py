from typing import Annotated

from asyncpg import Connection
from fastapi import APIRouter, Depends

from core.methods import get_connection
from .sale_order.api import router as sale_order_router

router = APIRouter(prefix="/sale_orders")
router.include_router(sale_order_router)


@router.get('/')
async def get_sale_orders(
    connection: Annotated[Connection, Depends(get_connection)]
):
    ...
