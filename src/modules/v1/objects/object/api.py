from typing import Annotated

from asyncpg import Connection
from fastapi import APIRouter, Depends, Body, Path

from core.methods import get_connection

router = APIRouter()


@router.post('/')
async def create_object(
    connection: Annotated[Connection, Depends(get_connection)],
    name: Annotated[str, Body(min_length=1)],
    is_active: Annotated[bool, Body()],
):
    ...


@router.get('/{object_id}')
async def get_object(
    connection: Annotated[Connection, Depends(get_connection)],
    object_id: Annotated[int, Path(ge=1)],
):
    ...


@router.put('/{object_id}')
async def update_object(
    connection: Annotated[Connection, Depends(get_connection)],
    object_id: Annotated[int, Path(ge=1)],
    name: Annotated[str, Body(min_length=1)],
    is_active: Annotated[bool, Body()],
):
    ...

