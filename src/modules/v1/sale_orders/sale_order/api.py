from typing import Annotated

from asyncpg import Connection
from fastapi import APIRouter, Depends, Body, Path

from core.methods import get_connection
from core.models.sale_orders import SaleOrderStatus
from .schemas import SaleOrderItemModel

router = APIRouter()


@router.post('/')
async def create_sale_order(
    supplier_id: Annotated[int, Body(ge=1)],
    name: Annotated[str, Body(min_length=1)],
    status: Annotated[SaleOrderStatus, Body()],
    items: Annotated[list[SaleOrderItemModel], Body()],
    connection: Annotated[Connection, Depends(get_connection)]
):
    ...


@router.get('/{sale_order_id}')
async def get_sale_order(
    sale_order_id: Annotated[int, Path(ge=1)],
    connection: Annotated[Connection, Depends(get_connection)]
):
    ...


@router.put('/{sale_order_id}')
async def update_sale_order(
    sale_order_id: Annotated[int, Path(ge=1)],
    supplier_id: Annotated[int, Body(ge=1)],
    name: Annotated[str, Body(min_length=1)],
    status: Annotated[SaleOrderStatus, Body()],
    items: Annotated[list[SaleOrderItemModel], Body()],
    connection: Annotated[Connection, Depends(get_connection)]
):
    # Можно изменять только если статус черновик
    ...


@router.delete('/{sale_order_id}')
async def delete_sale_order(
    sale_order_id: Annotated[int, Path(ge=1)],
    connection: Annotated[Connection, Depends(get_connection)]
):
    # Можно удалять только если статус черновик
    ...
