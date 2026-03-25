from typing import Annotated

from asyncpg import Connection
from everbase import Select
from fastapi import APIRouter, Depends
from sqlalchemy import func

from core.methods import get_connection
from core.models import Arrival, ArrivalItem
from .arrival.api import router as arrival_router
from .arrival.schemes import ArrivalModel, ArrivalItemWithIdModel

router = APIRouter(prefix="/arrivals")
router.include_router(arrival_router)


@router.get('/')
async def get_arrivals(
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
        .subquery("items_subquery")
    )

    arrivals = await (
        Select(
            Arrival.id,
            Arrival.supplier_id,
            Arrival.name,
            Arrival.status,
            Arrival.created_at,
            items_subquery.c.items
        )
        .outerjoin(items_subquery, Arrival.id == items_subquery.c.arrival_id)
        .fetch_all(
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

    return arrivals
