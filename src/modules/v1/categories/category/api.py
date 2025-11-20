from typing import Annotated

from asyncpg import Connection
from fastapi import APIRouter, Depends, Body, Path

from core.methods import get_connection

router = APIRouter()


@router.post('/')
async def create_category(
    connection: Annotated[Connection, Depends(get_connection)],
    name: Annotated[str, Body(min_length=1)],
    is_subcategory: Annotated[bool, Body()] = False,
):
    ...


@router.get('/{category_id}')
async def get_category(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1)],
):
    ...


@router.put('/{category_id}')
async def update_category(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1)],
    name: Annotated[str, Body(min_length=1)],
    is_subcategory: Annotated[bool, Body()] = False,
):
    ...


@router.delete('/{category_id}')
async def delete_category(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1)],
):
    ...


#  FIXME: Переместить в другую папку?


@router.put('/{category_id}/subcategory')
async def add_subcategory(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1)],
    subcategory_id: Annotated[int, Body(ge=1)],
):
    ...


@router.delete('/{category_id}/subcategory')
async def remove_subcategory(
    connection: Annotated[Connection, Depends(get_connection)],
    category_id: Annotated[int, Path(ge=1)],
    subcategory_id: Annotated[int, Body(ge=1)],
):
    ...
