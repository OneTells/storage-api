from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path

from core.exceptions import APIException
from core.methods import get_connection, get_current_user, require_permissions
from core.schemes import UserModel
from modules.operations.repositories import material_exists, production_order_exists, warehouse_exists
from modules.production_orders.production_order import repositories as production_order_repositories
from modules.production_orders.production_order.responses import PRODUCTION_ORDER_404, PRODUCTION_ORDER_MATERIAL_422
from modules.production_orders.production_order.schemes import (
    MaterialReservationAdd,
    MaterialReservationCancel,
    ProductionOrderCreate,
    ProductionOrderCreateResponse,
    ProductionOrderPatch,
)
from modules.production_orders.repositories import get_production_order_row, production_order_read_from_row
from modules.production_orders.schemes import ProductionOrderRead

router = APIRouter()


@router.post(
    "/",
    response_model=ProductionOrderCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions("production_order.create"))],
    summary="Создать производственный заказ",
)
async def create_production_order(
    connection: Annotated[Connection, Depends(get_connection)],
    user: Annotated[UserModel, Depends(get_current_user)],
    payload: Annotated[ProductionOrderCreate, Body()],
):
    all_wh = list(dict.fromkeys([*payload.warehouse_ids, payload.delivery_warehouse_id]))
    existing_wh = await production_order_repositories.fetch_existing_warehouse_ids(connection, all_wh)
    if set(all_wh) != existing_wh:
        raise APIException(status_code=404, code="WAREHOUSE_NOT_FOUND", message="Один из складов не найден")

    pids = [p.product_id for p in payload.products]
    if set(pids) != await production_order_repositories.fetch_existing_product_ids(connection, pids):
        raise APIException(status_code=404, code="PRODUCT_NOT_FOUND", message="Один из продуктов не найден")

    rids = [r.resource_id for r in payload.resources]
    if rids and set(rids) != await production_order_repositories.fetch_existing_resource_ids(connection, rids):
        raise APIException(status_code=404, code="RESOURCE_NOT_FOUND", message="Один из ресурсов не найден")

    eids = [w.employee_id for w in payload.workers]
    if eids and set(eids) != await production_order_repositories.fetch_existing_employee_ids(connection, eids):
        raise APIException(status_code=404, code="EMPLOYEE_NOT_FOUND", message="Один из сотрудников не найден")

    oid = await production_order_repositories.create_production_order(connection, user.id, payload)
    return ProductionOrderCreateResponse(id=oid)


@router.get(
    "/{production_order_id}",
    response_model=ProductionOrderRead,
    dependencies=[Depends(require_permissions("production_order.read"))],
    summary="Карточка производственного заказа",
    responses={404: PRODUCTION_ORDER_404},
)
async def get_production_order(
    connection: Annotated[Connection, Depends(get_connection)],
    production_order_id: Annotated[int, Path(ge=1, description="Идентификатор заказа")],
):
    row = await get_production_order_row(connection, production_order_id)
    if row is None:
        raise APIException(
            status_code=404,
            code="PRODUCTION_ORDER_NOT_FOUND",
            message="Производственный заказ не найден",
        )
    return production_order_read_from_row(row)


@router.patch(
    "/{production_order_id}",
    response_model=ProductionOrderRead,
    dependencies=[Depends(require_permissions("production_order.update"))],
    summary="Частично обновить производственный заказ",
    responses={404: PRODUCTION_ORDER_404},
)
async def patch_production_order(
    connection: Annotated[Connection, Depends(get_connection)],
    production_order_id: Annotated[int, Path(ge=1)],
    payload: Annotated[ProductionOrderPatch, Body()],
):
    row = await get_production_order_row(connection, production_order_id)
    if row is None:
        raise APIException(
            status_code=404,
            code="PRODUCTION_ORDER_NOT_FOUND",
            message="Производственный заказ не найден",
        )

    if payload.delivery_warehouse_id is not None:
        if not await warehouse_exists(connection, payload.delivery_warehouse_id):
            raise APIException(status_code=404, code="WAREHOUSE_NOT_FOUND", message="Склад не найден")

    if payload.warehouse_ids is not None:
        unique = list(dict.fromkeys(payload.warehouse_ids))
        if set(unique) != await production_order_repositories.fetch_existing_warehouse_ids(connection, unique):
            raise APIException(status_code=404, code="WAREHOUSE_NOT_FOUND", message="Один из складов не найден")

    if payload.products is not None:
        pids = [p.product_id for p in payload.products]
        if pids and set(pids) != await production_order_repositories.fetch_existing_product_ids(connection, pids):
            raise APIException(status_code=404, code="PRODUCT_NOT_FOUND", message="Один из продуктов не найден")

    if payload.resources is not None:
        rids = [r.resource_id for r in payload.resources]
        if rids and set(rids) != await production_order_repositories.fetch_existing_resource_ids(connection, rids):
            raise APIException(status_code=404, code="RESOURCE_NOT_FOUND", message="Один из ресурсов не найден")

    if payload.workers is not None:
        eids = [w.employee_id for w in payload.workers]
        if eids and set(eids) != await production_order_repositories.fetch_existing_employee_ids(connection, eids):
            raise APIException(status_code=404, code="EMPLOYEE_NOT_FOUND", message="Один из сотрудников не найден")

    await production_order_repositories.patch_production_order(connection, production_order_id, payload)

    updated = await get_production_order_row(connection, production_order_id)
    if updated is None:
        raise APIException(
            status_code=404,
            code="PRODUCTION_ORDER_NOT_FOUND",
            message="Производственный заказ не найден",
        )
    return production_order_read_from_row(updated)


@router.post(
    "/{production_order_id}/material-reservations/",
    status_code=204,
    response_model=None,
    dependencies=[Depends(require_permissions("production_order.update"))],
    summary="Увеличить резерв материала по заказу",
    responses={
        404: PRODUCTION_ORDER_404,
        422: PRODUCTION_ORDER_MATERIAL_422,
    },
)
async def add_material_reservation(
    connection: Annotated[Connection, Depends(get_connection)],
    production_order_id: Annotated[int, Path(ge=1)],
    payload: Annotated[MaterialReservationAdd, Body()],
):
    if not await production_order_exists(connection, production_order_id):
        raise APIException(
            status_code=404,
            code="PRODUCTION_ORDER_NOT_FOUND",
            message="Производственный заказ не найден",
        )

    if not await material_exists(connection, payload.material_id):
        raise APIException(status_code=404, code="MATERIAL_NOT_FOUND", message="Материал не найден")

    await production_order_repositories.add_material_reservation_quantity(
        connection, production_order_id, payload.material_id, payload.quantity
    )


@router.post(
    "/{production_order_id}/material-reservations/cancel/",
    status_code=204,
    response_model=None,
    dependencies=[Depends(require_permissions("production_order.update"))],
    summary="Уменьшить резерв материала по заказу",
    responses={
        404: PRODUCTION_ORDER_404,
        422: PRODUCTION_ORDER_MATERIAL_422,
    },
)
async def cancel_material_reservation(
    connection: Annotated[Connection, Depends(get_connection)],
    production_order_id: Annotated[int, Path(ge=1)],
    payload: Annotated[MaterialReservationCancel, Body()],
):
    if not await production_order_exists(connection, production_order_id):
        raise APIException(
            status_code=404,
            code="PRODUCTION_ORDER_NOT_FOUND",
            message="Производственный заказ не найден",
        )

    ok = await production_order_repositories.cancel_material_reservation_quantity(
        connection, production_order_id, payload.material_id, payload.quantity
    )
    if not ok:
        raise APIException(
            status_code=422,
            code="INSUFFICIENT_MATERIAL_RESERVATION",
            message="Недостаточно зарезервированного количества по материалу или материал не ведётся по заказу",
        )
