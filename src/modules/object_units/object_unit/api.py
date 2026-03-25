from typing import Annotated

from asyncpg import Connection
from fastapi import APIRouter, Depends, Path

from core.methods import get_connection

router = APIRouter()


@router.get('/{object_unit_id}/operation-logs')
async def get_operation_logs(
    connection: Annotated[Connection, Depends(get_connection)],
    object_unit_id: Annotated[int, Path(ge=1)]
):
    ...
