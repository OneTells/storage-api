from typing import Annotated

from asyncpg import Connection
from fastapi import APIRouter, Depends, Path

from core.methods import get_connection

router = APIRouter(prefix="/objects")


@router.get('/')
async def get_objects(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int | None, Path(ge=1)] = None,
):
    ...


@router.get('/{object_id}/object_units')
async def get_object_units(
    connection: Annotated[Connection, Depends(get_connection)],
    object_id: Annotated[int, Path(ge=1)]
):
    ...
