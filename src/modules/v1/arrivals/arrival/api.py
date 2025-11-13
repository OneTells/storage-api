from typing import Annotated

from asyncpg import Connection
from everbase import Insert, Select, Delete, Update
from fastapi import APIRouter, Depends, Body, Path, HTTPException
from sqlalchemy import func

from core.methods import get_connection
from core.models import ObjectUnit
from core.models.arrivals import ArrivalStatus, Arrival, ArrivalItem
from core.models.object_units import ObjectUnitStatus
from .schemes import ArrivalItemModel, ArrivalModel, ArrivalItemWithIdModel

router = APIRouter()


@router.post('/')
async def create_arrival(
    supplier_id: Annotated[int, Body(ge=1)],
    name: Annotated[str, Body(min_length=1)],
    status: Annotated[ArrivalStatus, Body()],
    items: Annotated[list[ArrivalItemModel], Body()],
    connection: Annotated[Connection, Depends(get_connection)]
):
    async with connection.transaction():
        arrival_id: int = await (
            Insert(Arrival)
            .values(
                supplier_id=supplier_id,
                name=name,
                status=status
            )
            .returning(Arrival.id)
            .fetch_one(connection, model=lambda x: x['id'])
        )

        for item in items:
            object_unit_id: int | None = None

            if status != ArrivalStatus.DRAFT:
                object_unit_id = await (
                    Insert(ObjectUnit)
                    .values(
                        object_id=item.object_id,
                        warehouse_id=item.warehouse_id,
                        status=ObjectUnitStatus.DEFAULT
                    )
                    .returning(ObjectUnit.id)
                    .fetch_one(connection, model=lambda x: x['id'])
                )

            await (
                Insert(ArrivalItem)
                .values(
                    arrival_id=arrival_id,
                    object_unit_id=object_unit_id,
                    object_id=item.object_id,
                    warehouse_id=item.warehouse_id,
                    price=item.price
                )
                .execute(connection)
            )

    return {'id': arrival_id}


@router.get('/{arrival_id}')
async def get_arrival(
    arrival_id: Annotated[int, Path(ge=1)],
    connection: Annotated[Connection, Depends(get_connection)]
):
    items_subquery = (
        Select(
            ArrivalItem.arrival_id,
            (
                func.array_agg(
                    func.row(
                        ArrivalItem.id,
                        ArrivalItem.object_unit_id,
                        ArrivalItem.object_id,
                        ArrivalItem.warehouse_id,
                        ArrivalItem.price
                    )
                )
                .filter(ArrivalItem.id.is_not(None))
                .label("items")
            )
        )
        .group_by(ArrivalItem.arrival_id)
        .where(ArrivalItem.arrival_id == arrival_id)
        .subquery("items_subquery")
    )

    arrival = await (
        Select(
            Arrival.id,
            Arrival.supplier_id,
            Arrival.name,
            Arrival.status,
            Arrival.created_at,
            items_subquery.c.items
        )
        .outerjoin(items_subquery, Arrival.id == items_subquery.c.arrival_id)
        .where(Arrival.id == arrival_id)
        .fetch_one(
            connection,
            model=lambda row: ArrivalModel(
                **row,
                items=sorted(map(
                    lambda x: ArrivalItemWithIdModel(
                        id=x[0], object_unit_id=x[1], object_id=x[2], warehouse_id=x[3], price=x[4]), row["items"] or []
                ), key=lambda x: x["id"])
            )
        )
    )

    if arrival is None:
        raise HTTPException(status_code=404, detail="Поступление не существует")

    return arrival


@router.put('/{arrival_id}')
async def update_arrival(
    arrival_id: Annotated[int, Path(ge=1)],
    supplier_id: Annotated[int, Body(ge=1)],
    name: Annotated[str, Body(min_length=1)],
    status: Annotated[ArrivalStatus, Body()],
    items: Annotated[list[ArrivalItemModel], Body()],
    connection: Annotated[Connection, Depends(get_connection)]
):
    response = await (
        Select(Arrival.status)
        .where(Arrival.id == arrival_id)
        .fetch_one(connection)
    )

    if response is None:
        raise HTTPException(status_code=404, detail="Поступление не существует")

    if response['status'] != ArrivalStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Поступление не может быть изменено")

    async with connection.transaction():
        await (
            Update(Arrival)
            .values(
                supplier_id=supplier_id,
                name=name,
                status=status
            )
            .where(Arrival.id == arrival_id)
            .execute(connection)
        )

        await (
            Delete(ArrivalItem)
            .where(ArrivalItem.arrival_id == arrival_id)
            .execute(connection)
        )

        for item in items:
            object_unit_id: int | None = None

            if status != ArrivalStatus.DRAFT:
                object_unit_id = await (
                    Insert(ObjectUnit)
                    .values(
                        object_id=item.object_id,
                        warehouse_id=item.warehouse_id,
                        status=ObjectUnitStatus.DEFAULT
                    )
                    .returning(ObjectUnit.id)
                    .fetch_one(connection, model=lambda x: x['id'])
                )

            await (
                Insert(ArrivalItem)
                .values(
                    arrival_id=arrival_id,
                    object_unit_id=object_unit_id,
                    object_id=item.object_id,
                    warehouse_id=item.warehouse_id,
                    price=item.price
                )
                .execute(connection)
            )


@router.delete('/{arrival_id}')
async def delete_arrival(
    arrival_id: Annotated[int, Path(ge=1)],
    connection: Annotated[Connection, Depends(get_connection)]
):
    response = await (
        Select(Arrival.status)
        .where(Arrival.id == arrival_id)
        .fetch_one(connection)
    )

    if response is None:
        raise HTTPException(status_code=404, detail="Поступление не существует")

    if response['status'] != ArrivalStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Поступление не может быть удалено")

    await (
        Delete(Arrival)
        .where(Arrival.id == arrival_id)
        .execute(connection)
    )
