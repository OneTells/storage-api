from typing import Annotated

from asyncpg import Connection
from fastapi import APIRouter, Depends, Body, Path

router = APIRouter()


@router.get('/{object_id}/object-units')
async def get_object_units(
    object_id: Annotated[int, Path(ge=1)]
):
    ...


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


@router.delete('/{object_id}')
async def delete_object(
    connection: Annotated[Connection, Depends(get_connection)],
    object_id: Annotated[int, Path(ge=1)],
    name: Annotated[str, Body(min_length=1)],
    is_active: Annotated[bool, Body()],
):
    # Нужна проверка, если нет записей, то можно удалить. То есть если не было прихода товаров
    ...
