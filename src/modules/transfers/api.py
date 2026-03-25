from typing import Annotated

from asyncpg import Connection
from fastapi import APIRouter, Depends

from core.methods import get_connection
from .transfer.api import router as transfer_router

router = APIRouter(prefix="/transfers")
router.include_router(transfer_router)


@router.get('/')
async def get_transfers(
    connection: Annotated[Connection, Depends(get_connection)]
):
    ...
