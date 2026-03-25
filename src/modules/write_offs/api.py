from typing import Annotated

from asyncpg import Connection
from fastapi import APIRouter, Depends

from core.methods import get_connection
from .write_off.api import router as write_off_router

router = APIRouter(prefix="/write-offs")
router.include_router(write_off_router)


@router.get('/')
async def get_write_offs(
    connection: Annotated[Connection, Depends(get_connection)]
):
    ...
