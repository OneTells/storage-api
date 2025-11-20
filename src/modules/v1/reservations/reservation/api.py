from typing import Annotated

from asyncpg import Connection
from fastapi import APIRouter, Depends, Body, Path

from core.methods import get_connection

router = APIRouter()


@router.post('/')
async def create_reservation(
    object_unit: Annotated[int, Body(ge=1)],
    connection: Annotated[Connection, Depends(get_connection)]
):
    ...


@router.get('/{reservation_id}')
async def get_reservation(
    reservation_id: Annotated[int, Path(ge=1)],
    connection: Annotated[Connection, Depends(get_connection)]
):
    # Нужен ли???
    ...


@router.delete('/{reservation_id}')
async def cancel_reservation(
    reservation_id: Annotated[int, Path(ge=1)],
    connection: Annotated[Connection, Depends(get_connection)]
):
    ...
