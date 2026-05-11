from datetime import datetime, UTC
from decimal import Decimal
from typing import Any

from asyncpg import Record
from everbase import Connection
from sqlalchemy import Delete, delete, func, literal_column, select, Select, Update
from sqlalchemy.dialects.postgresql import Insert, aggregate_order_by

from core.models import (
    Batch,
    InventoryAdjustment,
    InventoryAdjustmentItem,
    InventoryAdjustmentItemDetails,
    OperationStatus,
    StockOperation,
    StockOperationType,
    User,
)
from modules.operations.exceptions import InsufficientStockError, StockIntegrityError
from modules.operations.inventory_adjustment.schemes import InventoryAdjustmentCreate, InventoryAdjustmentUpdate
from modules.operations.repositories import (
    InsufficientBatchesForFifoError,
    adjust_batch_remaining,
    allocate_inventory_adjustment_details_fifo,
    insert_inbound_batch,
)
from modules.operations.utils import inventory_line_qty_delta


async def count_inventory_adjustments(
    connection: Connection,
    user_id: int | None,
    created_from: datetime | None,
    created_to: datetime | None,
    status: OperationStatus | None,
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
    if status is not None:
        stmt = stmt.where(InventoryAdjustment.status == status)

    return await connection.fetch_val(stmt, model=lambda x: int(x))


async def fetch_inventory_adjustments(
    connection: Connection,
    page: int,
    limit: int,
    user_id: int | None,
    created_from: datetime | None,
    created_to: datetime | None,
    status: OperationStatus | None,
) -> list[Record]:
    iai = (
        Select(
            InventoryAdjustmentItem.operation_id,
            func.json_agg(
                aggregate_order_by(
                    func.json_build_object(
                        "material_id",
                        InventoryAdjustmentItem.material_id,
                        "expected_qty",
                        InventoryAdjustmentItem.expected_qty,
                        "actual_qty",
                        InventoryAdjustmentItem.actual_qty,
                    ),
                    InventoryAdjustmentItem.id.asc(),
                ),
            ).label("items_json"),
        )
        .group_by(InventoryAdjustmentItem.operation_id)
    ).subquery("inv_adj_items_agg")
    stmt = (
        Select(
            StockOperation.id,
            StockOperation.name,
            StockOperation.performed_at,
            InventoryAdjustment.status,
            InventoryAdjustment.warehouse_id,
            InventoryAdjustment.description,
            StockOperation.created_by_id,
            User.name.label("created_by_user_name"),
            StockOperation.created_at,
            StockOperation.completed_at,
            StockOperation.cancelled_at,
            func.coalesce(iai.c.items_json, literal_column("'[]'::json")).label("items"),
        )
        .select_from(InventoryAdjustment)
        .join(StockOperation, StockOperation.id == InventoryAdjustment.operation_id)
        .join(User, User.id == StockOperation.created_by_id)
        .outerjoin(iai, iai.c.operation_id == StockOperation.id)
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

    if status is not None:
        stmt = stmt.where(InventoryAdjustment.status == status)

    return await connection.fetch(stmt)


async def get_inventory_adjustment(connection: Connection, operation_id: int) -> Record | None:
    iai = (
        Select(
            InventoryAdjustmentItem.operation_id,
            func.json_agg(
                aggregate_order_by(
                    func.json_build_object(
                        "material_id",
                        InventoryAdjustmentItem.material_id,
                        "expected_qty",
                        InventoryAdjustmentItem.expected_qty,
                        "actual_qty",
                        InventoryAdjustmentItem.actual_qty,
                    ),
                    InventoryAdjustmentItem.id.asc(),
                ),
            ).label("items_json"),
        )
        .group_by(InventoryAdjustmentItem.operation_id)
    ).subquery("inv_adj_items_agg")
    stmt = (
        Select(
            StockOperation.id,
            StockOperation.name,
            StockOperation.performed_at,
            InventoryAdjustment.status,
            InventoryAdjustment.warehouse_id,
            InventoryAdjustment.description,
            StockOperation.created_by_id,
            User.name.label("created_by_user_name"),
            StockOperation.created_at,
            StockOperation.completed_at,
            StockOperation.cancelled_at,
            func.coalesce(iai.c.items_json, literal_column("'[]'::json")).label("items"),
        )
        .select_from(InventoryAdjustment)
        .join(StockOperation, StockOperation.id == InventoryAdjustment.operation_id)
        .join(User, User.id == StockOperation.created_by_id)
        .outerjoin(iai, iai.c.operation_id == StockOperation.id)
        .where(StockOperation.type == StockOperationType.INVENTORY_ADJUSTMENT, StockOperation.id == operation_id)
        .order_by(StockOperation.id.desc())
    )

    return await connection.fetch_row(stmt)


async def create_inventory_adjustment(connection: Connection, user_id: int, payload: InventoryAdjustmentCreate) -> int:
    now = datetime.now(UTC)
    so_extra: dict[str, Any] = {}
    if payload.status == OperationStatus.COMPLETED:
        so_extra["completed_at"] = now
    elif payload.status == OperationStatus.CANCELLED:
        so_extra["cancelled_at"] = now

    async with connection.transaction():
        op_id = await connection.fetch_val(
            Insert(StockOperation)
            .values(
                type=StockOperationType.INVENTORY_ADJUSTMENT,
                name=payload.name,
                performed_at=payload.performed_at,
                created_by_id=user_id,
                **so_extra,
            )
            .returning(StockOperation.id)
        )

        await connection.execute(
            Insert(InventoryAdjustment).values(
                operation_id=op_id,
                warehouse_id=payload.warehouse_id,
                description=payload.description,
                status=payload.status,
            )
        )

        for it in payload.items:
            await connection.execute(
                Insert(InventoryAdjustmentItem).values(
                    operation_id=op_id,
                    material_id=it.material_id,
                    expected_qty=it.expected_qty,
                    actual_qty=it.actual_qty,
                )
            )

        if payload.status == OperationStatus.COMPLETED:
            await apply_inventory_adjustment_completed(connection, int(op_id))

    return int(op_id)


async def update_inventory_adjustment(connection: Connection, operation_id: int, payload: InventoryAdjustmentUpdate) -> None:
    now = datetime.now(UTC)

    async with connection.transaction():
        prev = await connection.fetch_row(
            Select(InventoryAdjustment.status).where(InventoryAdjustment.operation_id == operation_id)
        )
        if prev is None:
            return

        prev_status: OperationStatus = prev["status"]
        reverted_completed = False

        if payload.items is not None:
            if prev_status == OperationStatus.COMPLETED:
                await revert_inventory_adjustment_completed(connection, operation_id)
                reverted_completed = True
            await connection.execute(
                Delete(InventoryAdjustmentItem).where(InventoryAdjustmentItem.operation_id == operation_id)
            )

            for it in payload.items:
                await connection.execute(
                    Insert(InventoryAdjustmentItem).values(
                        operation_id=operation_id,
                        material_id=it.material_id,
                        expected_qty=it.expected_qty,
                        actual_qty=it.actual_qty,
                    )
                )

        if payload.status is not None:
            if payload.status == OperationStatus.COMPLETED and (
                prev_status != OperationStatus.COMPLETED or reverted_completed
            ):
                await apply_inventory_adjustment_completed(connection, operation_id)
            if (
                payload.status == OperationStatus.CANCELLED
                and prev_status == OperationStatus.COMPLETED
                and not reverted_completed
            ):
                await revert_inventory_adjustment_completed(connection, operation_id)
        elif reverted_completed and prev_status == OperationStatus.COMPLETED:
            await apply_inventory_adjustment_completed(connection, operation_id)

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


async def _delete_inv_adj_details_for_operation(connection: Connection, operation_id: int) -> None:
    item_ids = select(InventoryAdjustmentItem.id).where(InventoryAdjustmentItem.operation_id == operation_id)
    await connection.execute(
        delete(InventoryAdjustmentItemDetails).where(InventoryAdjustmentItemDetails.item_id.in_(item_ids))
    )


async def apply_inventory_adjustment_completed(connection: Connection, operation_id: int) -> None:
    hdr = await connection.fetch_row(
        Select(InventoryAdjustment.warehouse_id).where(InventoryAdjustment.operation_id == operation_id)
    )
    if hdr is None:
        raise StockIntegrityError("Инвентаризация не найдена")
    wh = int(hdr["warehouse_id"])

    await _delete_inv_adj_details_for_operation(connection, operation_id)

    items = await connection.fetch(
        Select(
            InventoryAdjustmentItem.id,
            InventoryAdjustmentItem.material_id,
            InventoryAdjustmentItem.expected_qty,
            InventoryAdjustmentItem.actual_qty,
        )
        .where(InventoryAdjustmentItem.operation_id == operation_id)
        .order_by(InventoryAdjustmentItem.id.asc())
    )

    for it in items:
        item_id = int(it["id"])
        mat = int(it["material_id"])
        exp: Decimal = it["expected_qty"]
        act: Decimal = it["actual_qty"]
        diff = inventory_line_qty_delta(expected_qty=exp, actual_qty=act)
        if diff == 0:
            continue
        if diff > 0:
            bid = await insert_inbound_batch(connection, warehouse_id=wh, material_id=mat, quantity=diff)
            await connection.execute(
                Insert(InventoryAdjustmentItemDetails).values(
                    item_id=item_id,
                    batch_id=bid,
                    quantity=-diff,
                )
            )
        else:
            need = abs(diff)
            try:
                slices = await allocate_inventory_adjustment_details_fifo(connection, wh, mat, need)
            except InsufficientBatchesForFifoError as e:
                raise InsufficientStockError("Недостаточно партий под списание расхождения") from e
            for batch_id, q in slices:
                await adjust_batch_remaining(connection, batch_id, -q)
                await connection.execute(
                    Insert(InventoryAdjustmentItemDetails).values(
                        item_id=item_id,
                        batch_id=batch_id,
                        quantity=q,
                    )
                )


async def revert_inventory_adjustment_completed(connection: Connection, operation_id: int) -> None:
    item_ids = select(InventoryAdjustmentItem.id).where(InventoryAdjustmentItem.operation_id == operation_id)
    details = await connection.fetch(
        Select(InventoryAdjustmentItemDetails.batch_id, InventoryAdjustmentItemDetails.quantity)
        .where(InventoryAdjustmentItemDetails.item_id.in_(item_ids))
    )
    for d in details:
        qty: Decimal = d["quantity"]
        bid = int(d["batch_id"])
        if qty < 0:
            await connection.execute(Delete(Batch).where(Batch.id == bid))
        else:
            await adjust_batch_remaining(connection, bid, qty)
    await _delete_inv_adj_details_for_operation(connection, operation_id)
