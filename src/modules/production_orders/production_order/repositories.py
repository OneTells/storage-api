from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from everbase import Connection
from sqlalchemy import Delete, Select, Update
from sqlalchemy.dialects.postgresql import Insert

from core.models import (
    Employee,
    Product,
    ProductionOrder,
    ProductionOrderMaterial,
    ProductionOrderProduct,
    ProductionOrderResource,
    ProductionOrderStatus,
    ProductionOrderWorker,
    ProductionOrderWriteOffWarehouse,
    Resource,
    Warehouse,
)

from modules.production_orders.production_order.schemes import ProductionOrderCreate, ProductionOrderPatch


async def fetch_existing_product_ids(connection: Connection, product_ids: list[int]) -> set[int]:
    if not product_ids:
        return set()
    q = Select(Product.id).where(Product.id.in_(product_ids))
    rows = await connection.fetch(q)
    return {int(r[0]) for r in rows}


async def fetch_existing_resource_ids(connection: Connection, resource_ids: list[int]) -> set[int]:
    if not resource_ids:
        return set()
    q = Select(Resource.id).where(Resource.id.in_(resource_ids))
    rows = await connection.fetch(q)
    return {int(r[0]) for r in rows}


async def fetch_existing_employee_ids(connection: Connection, employee_ids: list[int]) -> set[int]:
    if not employee_ids:
        return set()
    q = Select(Employee.id).where(Employee.id.in_(employee_ids))
    rows = await connection.fetch(q)
    return {int(r[0]) for r in rows}


async def fetch_existing_warehouse_ids(connection: Connection, warehouse_ids: list[int]) -> set[int]:
    if not warehouse_ids:
        return set()
    q = Select(Warehouse.id).where(Warehouse.id.in_(warehouse_ids))
    rows = await connection.fetch(q)
    return {int(r[0]) for r in rows}


async def create_production_order(connection: Connection, user_id: int, payload: ProductionOrderCreate) -> int:
    async with connection.transaction():
        order_id = await connection.fetch_val(
            Insert(ProductionOrder)
            .values(
                performed_at=payload.performed_at,
                warehouse_id=payload.delivery_warehouse_id,
                comment="",
                status=ProductionOrderStatus.PLAN,
                created_by_id=user_id,
            )
            .returning(ProductionOrder.id)
        )
        oid = int(order_id)

        if payload.products:
            await connection.execute(
                Insert(ProductionOrderProduct).values(
                    [{"order_id": oid, "product_id": p.product_id, "quantity": p.quantity} for p in payload.products]
                )
            )

        if payload.resources:
            await connection.execute(
                Insert(ProductionOrderResource).values(
                    [{"order_id": oid, "resource_id": r.resource_id, "quantity": r.quantity} for r in payload.resources]
                )
            )

        if payload.workers:
            await connection.execute(
                Insert(ProductionOrderWorker).values(
                    [
                        {
                            "order_id": oid,
                            "employee_id": w.employee_id,
                            "hours_worked": w.hours_worked,
                            "hourly_rate": w.hourly_rate,
                        }
                        for w in payload.workers
                    ]
                )
            )

        unique_wh = list(dict.fromkeys(payload.warehouse_ids))
        if unique_wh:
            await connection.execute(
                Insert(ProductionOrderWriteOffWarehouse).values(
                    [{"order_id": oid, "warehouse_id": wid} for wid in unique_wh]
                )
            )

    return oid


async def patch_production_order(connection: Connection, order_id: int, payload: ProductionOrderPatch) -> None:
    now = datetime.now(UTC)
    async with connection.transaction():
        if payload.products is not None:
            await connection.execute(Delete(ProductionOrderProduct).where(ProductionOrderProduct.order_id == order_id))
            if payload.products:
                await connection.execute(
                    Insert(ProductionOrderProduct).values(
                        [
                            {"order_id": order_id, "product_id": p.product_id, "quantity": p.quantity}
                            for p in payload.products
                        ]
                    )
                )

        if payload.resources is not None:
            await connection.execute(
                Delete(ProductionOrderResource).where(ProductionOrderResource.order_id == order_id)
            )
            if payload.resources:
                await connection.execute(
                    Insert(ProductionOrderResource).values(
                        [
                            {"order_id": order_id, "resource_id": r.resource_id, "quantity": r.quantity}
                            for r in payload.resources
                        ]
                    )
                )

        if payload.workers is not None:
            await connection.execute(Delete(ProductionOrderWorker).where(ProductionOrderWorker.order_id == order_id))
            if payload.workers:
                await connection.execute(
                    Insert(ProductionOrderWorker).values(
                        [
                            {
                                "order_id": order_id,
                                "employee_id": w.employee_id,
                                "hours_worked": w.hours_worked,
                                "hourly_rate": w.hourly_rate,
                            }
                            for w in payload.workers
                        ]
                    )
                )

        if payload.warehouse_ids is not None:
            await connection.execute(
                Delete(ProductionOrderWriteOffWarehouse).where(
                    ProductionOrderWriteOffWarehouse.order_id == order_id
                )
            )
            unique_wh = list(dict.fromkeys(payload.warehouse_ids))
            if unique_wh:
                await connection.execute(
                    Insert(ProductionOrderWriteOffWarehouse).values(
                        [{"order_id": order_id, "warehouse_id": wid} for wid in unique_wh]
                    )
                )

        po_vals: dict[str, Any] = {}
        if payload.performed_at is not None:
            po_vals["performed_at"] = payload.performed_at
        if payload.delivery_warehouse_id is not None:
            po_vals["warehouse_id"] = payload.delivery_warehouse_id
        if payload.comment is not None:
            po_vals["comment"] = payload.comment
        if payload.status is not None:
            po_vals["status"] = payload.status
            if payload.status == ProductionOrderStatus.COMPLETED:
                po_vals["completed_at"] = now
            elif payload.status == ProductionOrderStatus.CLOSED:
                po_vals["closed_at"] = now
            elif payload.status == ProductionOrderStatus.CANCELLED:
                po_vals["cancelled_at"] = now

        if po_vals:
            await connection.execute(Update(ProductionOrder).where(ProductionOrder.id == order_id).values(**po_vals))


async def add_material_reservation_quantity(
    connection: Connection,
    order_id: int,
    material_id: int,
    quantity: Decimal,
) -> None:
    async with connection.transaction():
        row = await connection.fetch_row(
            Select(
                ProductionOrderMaterial.id,
                ProductionOrderMaterial.quantity,
                ProductionOrderMaterial.reservation_quantity,
            ).where(
                ProductionOrderMaterial.order_id == order_id,
                ProductionOrderMaterial.material_id == material_id,
            )
        )
        if row is None:
            await connection.execute(
                Insert(ProductionOrderMaterial).values(
                    order_id=order_id,
                    material_id=material_id,
                    quantity=Decimal(0),
                    reservation_quantity=quantity,
                )
            )
        else:
            new_r = Decimal(row["reservation_quantity"]) + quantity
            await connection.execute(
                Update(ProductionOrderMaterial)
                .where(ProductionOrderMaterial.id == row["id"])
                .values(reservation_quantity=new_r)
            )


async def cancel_material_reservation_quantity(
    connection: Connection,
    order_id: int,
    material_id: int,
    quantity: Decimal,
) -> bool:
    """Возвращает False, если строки нет или резерва меньше quantity."""
    async with connection.transaction():
        row = await connection.fetch_row(
            Select(ProductionOrderMaterial.id, ProductionOrderMaterial.reservation_quantity).where(
                ProductionOrderMaterial.order_id == order_id,
                ProductionOrderMaterial.material_id == material_id,
            )
        )
        if row is None:
            return False
        cur = Decimal(row["reservation_quantity"])
        if cur < quantity:
            return False
        new_r = cur - quantity
        await connection.execute(
            Update(ProductionOrderMaterial)
            .where(ProductionOrderMaterial.id == row["id"])
            .values(reservation_quantity=new_r)
        )
    return True
