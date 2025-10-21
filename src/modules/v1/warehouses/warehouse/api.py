from typing import Annotated

from asyncpg import Connection, Record
from everbase import Insert, Select, Update
from fastapi import APIRouter, Depends, Body, Path, HTTPException

from core.methods import get_connection
from core.models import Warehouse
from ..schemes import WarehouseModel

router = APIRouter()


@router.post("/")
async def create_warehouse(
    name: Annotated[str, Body(min_length=1)],
    address: Annotated[str, Body(min_length=1)],
    is_active: Annotated[bool, Body()],
    connection: Annotated[Connection, Depends(get_connection)]
):
    response: Record = await (
        Insert(Warehouse)
        .values(
            name=name,
            address=address,
            is_active=is_active
        )
        .returning(Warehouse.id)
        .fetch_one(connection)
    )

    return {'id': response['id']}


@router.get("/{warehouse_id}")
async def get_warehouse(
    warehouse_id: Annotated[int, Path(ge=1)],
    connection: Annotated[Connection, Depends(get_connection)]
):
    response = await (
        Select(
            Warehouse.id,
            Warehouse.name,
            Warehouse.address,
            Warehouse.is_active,
            Warehouse.created_at
        )
        .where(Warehouse.id == warehouse_id)
        .fetch_one(connection, model=WarehouseModel)
    )

    if response is None:
        raise HTTPException(status_code=404, detail="Склад не существует")

    return response


@router.put("/{warehouse_id}")
async def update_warehouse(
    warehouse_id: Annotated[int, Path(ge=1)],
    name: Annotated[str, Body(min_length=1)],
    address: Annotated[str, Body(min_length=1)],
    is_active: Annotated[bool, Body()],
    connection: Annotated[Connection, Depends(get_connection)]
):
    response = await (
        Select(True)
        .select_from(Warehouse)
        .where(Warehouse.id == warehouse_id)
        .fetch_one(connection)
    )

    if response is None:
        raise HTTPException(status_code=404, detail="Склад не существует")

    await (
        Update(Warehouse)
        .values(
            name=name,
            address=address,
            is_active=is_active
        )
        .where(Warehouse.id == warehouse_id)
        .execute(connection)
    )

    return None
