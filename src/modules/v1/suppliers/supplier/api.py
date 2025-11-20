from typing import Annotated

from asyncpg import Connection, Record
from everbase import Insert, Select, Update
from fastapi import APIRouter, Depends, Body, Path, HTTPException

from core.methods import get_connection
from core.models import Supplier
from ..schemes import SupplierModel

router = APIRouter()


@router.post("/")
async def create_supplier(
    name: Annotated[str, Body(min_length=1)],
    is_active: Annotated[bool, Body()],
    connection: Annotated[Connection, Depends(get_connection)]
):
    response: Record = await (
        Insert(Supplier)
        .values(
            name=name,
            is_active=is_active
        )
        .returning(Supplier.id)
        .fetch_one(connection)
    )

    return {'id': response['id']}


@router.get("/{supplier_id}")
async def get_supplier(
    supplier_id: Annotated[int, Path(ge=1)],
    connection: Annotated[Connection, Depends(get_connection)]
):
    response = await (
        Select(
            Supplier.id,
            Supplier.name,
            Supplier.is_active,
            Supplier.created_at
        )
        .where(Supplier.id == supplier_id)
        .fetch_one(connection, model=SupplierModel)
    )

    if response is None:
        raise HTTPException(status_code=404, detail="Поставщик не существует")

    return response


@router.put("/{supplier_id}")
async def update_supplier(
    supplier_id: Annotated[int, Path(ge=1)],
    name: Annotated[str, Body(min_length=1)],
    is_active: Annotated[bool, Body()],
    connection: Annotated[Connection, Depends(get_connection)]
):
    response = await (
        Select(True)
        .select_from(Supplier)
        .where(Supplier.id == supplier_id)
        .fetch_one(connection)
    )

    if response is None:
        raise HTTPException(status_code=404, detail="Склад не существует")

    await (
        Update(Supplier)
        .values(
            name=name,
            is_active=is_active
        )
        .where(Supplier.id == supplier_id)
        .execute(connection)
    )

    return None
