from typing import Annotated

from asyncpg import Connection
from everbase import Select
from fastapi import APIRouter, Depends

from core.methods import get_connection
from core.models import Warehouse
from .warehouse.api import router as warehouse_router
from .schemes import WarehouseModel

router = APIRouter(prefix="/warehouses")
router.include_router(warehouse_router)


@router.get('/')
async def get_warehouses(
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
        .fetch_all(connection, model=WarehouseModel)
    )

    return response
