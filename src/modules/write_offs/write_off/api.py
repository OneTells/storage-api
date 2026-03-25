from typing import Annotated

from asyncpg import Connection
from fastapi import APIRouter, Depends, Body, Path

from core.methods import get_connection
from core.models.write_offs import WriteOffStatus
from .schemes import WriteOffItemModel

router = APIRouter()


@router.post('/')
async def create_write_off(
    supplier_id: Annotated[int, Body(ge=1)],
    name: Annotated[str, Body(min_length=1)],
    status: Annotated[WriteOffStatus, Body()],
    items: Annotated[list[WriteOffItemModel], Body()],
    connection: Annotated[Connection, Depends(get_connection)]
):
    ...


@router.get('/{write_off_id}')
async def get_write_off(
    write_off_id: Annotated[int, Path(ge=1)],
    connection: Annotated[Connection, Depends(get_connection)]
):
    ...


@router.put('/{write_off_id}')
async def update_write_off(
    write_off_id: Annotated[int, Path(ge=1)],
    supplier_id: Annotated[int, Body(ge=1)],
    name: Annotated[str, Body(min_length=1)],
    status: Annotated[WriteOffStatus, Body()],
    items: Annotated[list[WriteOffItemModel], Body()],
    connection: Annotated[Connection, Depends(get_connection)]
):
    # Можно изменять только если статус черновик
    ...


@router.delete('/{write_off_id}')
async def delete_write_off(
    write_off_id: Annotated[int, Path(ge=1)],
    connection: Annotated[Connection, Depends(get_connection)]
):
    # Можно удалять только если статус черновик
    ...
