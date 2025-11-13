from typing import Annotated

from asyncpg import Connection
from fastapi import APIRouter, Depends, Body, Path

from core.methods import get_connection
from core.models.transfers import TransferStatus
from .schemes import TransferItemModel

router = APIRouter()


@router.post('/')
async def create_transfer(
    supplier_id: Annotated[int, Body(ge=1)],
    name: Annotated[str, Body(min_length=1)],
    status: Annotated[TransferStatus, Body()],
    items: Annotated[list[TransferItemModel], Body()],
    connection: Annotated[Connection, Depends(get_connection)]
):
    ...


@router.get('/{transfer_id}')
async def get_transfer(
    transfer_id: Annotated[int, Path(ge=1)],
    connection: Annotated[Connection, Depends(get_connection)]
):
    ...


@router.put('/{transfer_id}')
async def update_transfer(
    transfer_id: Annotated[int, Path(ge=1)],
    supplier_id: Annotated[int, Body(ge=1)],
    name: Annotated[str, Body(min_length=1)],
    status: Annotated[TransferStatus, Body()],
    items: Annotated[list[TransferItemModel], Body()],
    connection: Annotated[Connection, Depends(get_connection)]
):
    # Можно изменять только если статус черновик
    ...


@router.delete('/{transfer_id}')
async def delete_transfer(
    transfer_id: Annotated[int, Path(ge=1)],
    connection: Annotated[Connection, Depends(get_connection)]
):
    # Можно удалять только если статус черновик
    ...
