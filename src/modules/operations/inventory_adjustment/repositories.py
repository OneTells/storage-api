from datetime import datetime, UTC
from typing import Any

from asyncpg import Record
from everbase import Connection
from sqlalchemy import Delete, func, Select, Update
from sqlalchemy.dialects.postgresql import Insert

from core.models import (
    InventoryAdjustment,
    InventoryAdjustmentItem,
    InventoryAdjustmentItemDetails,
    OperationStatus,
    StockOperation,
    StockOperationType,
)
from modules.operations.inventory_adjustment.schemes import InventoryAdjustmentCreate, InventoryAdjustmentUpdate
from modules.operations.repositories import allocate_inventory_adjustment_details_fifo


async def count_inventory_adjustments(
    connection: Connection,
    user_id: int | None,
    created_from: datetime | None,
    created_to: datetime | None,
) -> int:
    stmt = (
        Select(func.count())
        .select_from(InventoryAdjustment)
        .join(StockOperation, StockOperation.id == InventoryAdjustment.operation_id)
        .where(StockOperation.type == StockOperationType.INVENTORY_ADJUSTMENT)
    )
    if user_id is not None:
        stmt = stmt.where(StockOperation.created_by_id == user_id)
    if created_from is not None:
        stmt = stmt.where(StockOperation.created_at >= created_from)
    if created_to is not None:
        stmt = stmt.where(StockOperation.created_at <= created_to)

    return await connection.fetch_val(stmt, model=lambda x: int(x))


async def fetch_inventory_adjustments(
    connection: Connection,
    page: int,
    limit: int,
    user_id: int | None,
    created_from: datetime | None,
    created_to: datetime | None,
) -> list[Record]:
    stmt = (
        Select(
            StockOperation.id,
            StockOperation.name,
            StockOperation.performed_at,
            InventoryAdjustment.status,
            InventoryAdjustment.warehouse_id,
            InventoryAdjustment.description,
            StockOperation.created_by_id,
            StockOperation.created_at,
            StockOperation.completed_at,
            StockOperation.cancelled_at,
        )
        .select_from(InventoryAdjustment)
        .join(StockOperation, StockOperation.id == InventoryAdjustment.operation_id)
        .where(StockOperation.type == StockOperationType.INVENTORY_ADJUSTMENT)
        .order_by(StockOperation.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )

    if user_id is not None:
        stmt = stmt.where(StockOperation.created_by_id == user_id)

    if created_from is not None:
        stmt = stmt.where(StockOperation.created_at >= created_from)

    if created_to is not None:
        stmt = stmt.where(StockOperation.created_at <= created_to)

    return await connection.fetch(stmt)


async def get_inventory_adjustment(connection: Connection, operation_id: int) -> Record | None:
    stmt = (
        Select(
            StockOperation.id,
            StockOperation.name,
            StockOperation.performed_at,
            InventoryAdjustment.status,
            InventoryAdjustment.warehouse_id,
            InventoryAdjustment.description,
            StockOperation.created_by_id,
            StockOperation.created_at,
            StockOperation.completed_at,
            StockOperation.cancelled_at,
        )
        .select_from(InventoryAdjustment)
        .join(StockOperation, StockOperation.id == InventoryAdjustment.operation_id)
        .where(StockOperation.type == StockOperationType.INVENTORY_ADJUSTMENT, StockOperation.id == operation_id)
        .order_by(StockOperation.id.desc())
    )

    return await connection.fetch_row(stmt)


async def create_inventory_adjustment(connection: Connection, user_id: int, payload: InventoryAdjustmentCreate) -> int:
    async with connection.transaction():
        op_id = await connection.fetch_val(
            Insert(StockOperation)
            .values(
                type=StockOperationType.INVENTORY_ADJUSTMENT,
                name=payload.name,
                performed_at=payload.performed_at,
                created_by_id=user_id,
            )
            .returning(StockOperation.id)
        )

        await connection.execute(
            Insert(InventoryAdjustment).values(
                operation_id=op_id,
                warehouse_id=payload.warehouse_id,
                description=payload.description,
                status=OperationStatus.DRAFT,
            )
        )

        for it in payload.items:
            item_id = await connection.fetch_val(
                Insert(InventoryAdjustmentItem)
                .values(
                    operation_id=op_id,
                    material_id=it.material_id,
                    expected_qty=it.expected_qty,
                    actual_qty=it.actual_qty,
                )
                .returning(InventoryAdjustmentItem.id)
            )

            detail_rows = await allocate_inventory_adjustment_details_fifo(
                connection,
                int(payload.warehouse_id),
                int(it.material_id),
                it.actual_qty,
            )

            for batch_id, qty in detail_rows:
                await connection.execute(
                    Insert(InventoryAdjustmentItemDetails).values(
                        item_id=item_id,
                        batch_id=batch_id,
                        quantity=qty,
                    )
                )

    return int(op_id)


async def update_inventory_adjustment(connection: Connection, operation_id: int, payload: InventoryAdjustmentUpdate) -> None:
    now = datetime.now(UTC)

    async with connection.transaction():
        so_vals: dict[str, Any] = {}

        if payload.name is not None:
            so_vals["name"] = payload.name

        if payload.performed_at is not None:
            so_vals["performed_at"] = payload.performed_at

        if payload.status is not None:
            if payload.status == OperationStatus.COMPLETED:
                so_vals["completed_at"] = now
            elif payload.status == OperationStatus.CANCELLED:
                so_vals["cancelled_at"] = now

        if so_vals:
            await connection.execute(Update(StockOperation).where(StockOperation.id == operation_id).values(**so_vals))

        i_vals: dict[str, Any] = {}
        if payload.warehouse_id is not None:
            i_vals["warehouse_id"] = payload.warehouse_id

        if payload.description is not None:
            i_vals["description"] = payload.description

        if payload.status is not None:
            i_vals["status"] = payload.status

        if i_vals:
            await connection.execute(
                Update(InventoryAdjustment).where(InventoryAdjustment.operation_id == operation_id).values(**i_vals)
            )

        if payload.items is not None:
            wh: int
            if payload.warehouse_id is not None:
                wh = int(payload.warehouse_id)
            else:
                cur = await connection.fetch_row(
                    Select(InventoryAdjustment.warehouse_id).where(
                        InventoryAdjustment.operation_id == operation_id
                    )
                )
                assert cur is not None
                wh = int(cur["warehouse_id"])

            await connection.execute(
                Delete(InventoryAdjustmentItem).where(InventoryAdjustmentItem.operation_id == operation_id)
            )

            for it in payload.items:
                item_id = await connection.fetch_val(
                    Insert(InventoryAdjustmentItem)
                    .values(
                        operation_id=operation_id,
                        material_id=it.material_id,
                        expected_qty=it.expected_qty,
                        actual_qty=it.actual_qty,
                    )
                    .returning(InventoryAdjustmentItem.id)
                )

                detail_rows = await allocate_inventory_adjustment_details_fifo(
                    connection,
                    wh,
                    int(it.material_id),
                    it.actual_qty,
                )

                for batch_id, qty in detail_rows:
                    await connection.execute(
                        Insert(InventoryAdjustmentItemDetails).values(
                            item_id=item_id,
                            batch_id=batch_id,
                            quantity=qty,
                        )
                    )
