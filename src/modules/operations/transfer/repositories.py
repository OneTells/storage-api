from datetime import UTC, datetime
from typing import Any

from asyncpg import Record
from everbase import Connection
from sqlalchemy import Delete, literal_column, Select, Update, func
from sqlalchemy.dialects.postgresql import Insert, aggregate_order_by

from core.models import Batch, OperationStatus, StockOperation, StockOperationType, Transfer, TransferItem, User

from modules.operations.exceptions import InsufficientStockError, StockIntegrityError
from modules.operations.repositories import (
    adjust_batch_remaining,
    find_fifo_batch_covering_quantity,
    insert_inbound_batch,
)
from modules.operations.transfer.schemes import TransferCreate, TransferUpdate


async def count_transfers(
    connection: Connection,
    user_id: int | None,
    created_from: datetime | None,
    created_to: datetime | None,
    status: OperationStatus | None,
) -> int:
    stmt = (
        Select(func.count())
        .select_from(Transfer)
        .join(StockOperation, StockOperation.id == Transfer.operation_id)
        .where(StockOperation.type == StockOperationType.TRANSFER)
    )

    if user_id is not None:
        stmt = stmt.where(StockOperation.created_by_id == user_id)

    if created_from is not None:
        stmt = stmt.where(StockOperation.created_at >= created_from)

    if created_to is not None:
        stmt = stmt.where(StockOperation.created_at <= created_to)

    if status is not None:
        stmt = stmt.where(Transfer.status == status)

    return await connection.fetch_val(stmt, model=lambda x: int(x))


async def fetch_transfers(
    connection: Connection,
    page: int,
    limit: int,
    user_id: int | None,
    created_from: datetime | None,
    created_to: datetime | None,
    status: OperationStatus | None,
) -> list[Record]:
    tri = (
        Select(
            TransferItem.operation_id,
            func.json_agg(
                aggregate_order_by(
                    func.json_build_object(
                        "material_id",
                        TransferItem.material_id,
                        "quantity",
                        TransferItem.quantity,
                        "old_batch_id",
                        TransferItem.old_batch_id,
                        "new_batch_id",
                        TransferItem.new_batch_id,
                    ),
                    TransferItem.id.asc(),
                ),
            ).label("items_json"),
        )
        .group_by(TransferItem.operation_id)
    ).subquery("transfer_items_agg")
    stmt = (
        Select(
            StockOperation.id,
            StockOperation.name,
            StockOperation.performed_at,
            Transfer.status,
            Transfer.from_warehouse_id,
            Transfer.to_warehouse_id,
            StockOperation.created_by_id,
            User.name.label("created_by_user_name"),
            StockOperation.created_at,
            StockOperation.completed_at,
            StockOperation.cancelled_at,
            func.coalesce(tri.c.items_json, literal_column("'[]'::json")).label("items"),
        )
        .select_from(Transfer)
        .join(StockOperation, StockOperation.id == Transfer.operation_id)
        .join(User, User.id == StockOperation.created_by_id)
        .outerjoin(tri, tri.c.operation_id == StockOperation.id)
        .where(StockOperation.type == StockOperationType.TRANSFER)
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
        stmt = stmt.where(Transfer.status == status)

    return await connection.fetch(stmt)


async def get_transfer(connection: Connection, operation_id: int) -> Record | None:
    tri = (
        Select(
            TransferItem.operation_id,
            func.json_agg(
                aggregate_order_by(
                    func.json_build_object(
                        "material_id",
                        TransferItem.material_id,
                        "quantity",
                        TransferItem.quantity,
                        "old_batch_id",
                        TransferItem.old_batch_id,
                        "new_batch_id",
                        TransferItem.new_batch_id,
                    ),
                    TransferItem.id.asc(),
                ),
            ).label("items_json"),
        )
        .group_by(TransferItem.operation_id)
    ).subquery("transfer_items_agg")
    stmt = (
        Select(
            StockOperation.id,
            StockOperation.name,
            StockOperation.performed_at,
            Transfer.status,
            Transfer.from_warehouse_id,
            Transfer.to_warehouse_id,
            StockOperation.created_by_id,
            User.name.label("created_by_user_name"),
            StockOperation.created_at,
            StockOperation.completed_at,
            StockOperation.cancelled_at,
            func.coalesce(tri.c.items_json, literal_column("'[]'::json")).label("items"),
        )
        .select_from(Transfer)
        .join(StockOperation, StockOperation.id == Transfer.operation_id)
        .join(User, User.id == StockOperation.created_by_id)
        .outerjoin(tri, tri.c.operation_id == StockOperation.id)
        .where(StockOperation.type == StockOperationType.TRANSFER, StockOperation.id == operation_id)
        .order_by(StockOperation.id.desc())
    )

    return await connection.fetch_row(stmt)


async def create_transfer(connection: Connection, user_id: int, payload: TransferCreate) -> int:
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
                type=StockOperationType.TRANSFER,
                name=payload.name,
                performed_at=payload.performed_at,
                created_by_id=user_id,
                **so_extra,
            )
            .returning(StockOperation.id)
        )

        await connection.execute(
            Insert(Transfer).values(
                operation_id=op_id,
                from_warehouse_id=payload.from_warehouse_id,
                to_warehouse_id=payload.to_warehouse_id,
                status=payload.status,
            )
        )

        for it in payload.items:
            await connection.execute(
                Insert(TransferItem).values(
                    operation_id=op_id,
                    material_id=it.material_id,
                    quantity=it.quantity,
                    old_batch_id=None,
                    new_batch_id=None,
                )
            )

        if payload.status == OperationStatus.COMPLETED:
            await apply_transfer_completed(connection, int(op_id))

    return int(op_id)


async def update_transfer(connection: Connection, operation_id: int, payload: TransferUpdate) -> None:
    now = datetime.now(UTC)

    async with connection.transaction():
        prev = await connection.fetch_row(Select(Transfer.status).where(Transfer.operation_id == operation_id))
        if prev is None:
            return

        prev_status: OperationStatus = prev["status"]
        reverted_completed = False

        if payload.items is not None:
            if prev_status == OperationStatus.COMPLETED:
                await revert_transfer_completed(connection, operation_id)
                reverted_completed = True
            await connection.execute(Delete(TransferItem).where(TransferItem.operation_id == operation_id))

            for it in payload.items:
                await connection.execute(
                    Insert(TransferItem).values(
                        operation_id=operation_id,
                        material_id=it.material_id,
                        quantity=it.quantity,
                        old_batch_id=None,
                        new_batch_id=None,
                    )
                )

        if payload.status is not None:
            if payload.status == OperationStatus.COMPLETED and (
                prev_status != OperationStatus.COMPLETED or reverted_completed
            ):
                await apply_transfer_completed(connection, operation_id)
            if (
                payload.status == OperationStatus.CANCELLED
                and prev_status == OperationStatus.COMPLETED
                and not reverted_completed
            ):
                await revert_transfer_completed(connection, operation_id)
        elif reverted_completed and prev_status == OperationStatus.COMPLETED:
            await apply_transfer_completed(connection, operation_id)

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

        t_vals: dict[str, Any] = {}

        if payload.from_warehouse_id is not None:
            t_vals["from_warehouse_id"] = payload.from_warehouse_id

        if payload.to_warehouse_id is not None:
            t_vals["to_warehouse_id"] = payload.to_warehouse_id

        if payload.status is not None:
            t_vals["status"] = payload.status

        if t_vals:
            await connection.execute(Update(Transfer).where(Transfer.operation_id == operation_id).values(**t_vals))


async def apply_transfer_completed(connection: Connection, operation_id: int) -> None:
    hdr = await connection.fetch_row(
        Select(Transfer.from_warehouse_id, Transfer.to_warehouse_id).where(
            Transfer.operation_id == operation_id
        )
    )
    if hdr is None:
        raise StockIntegrityError("Перемещение не найдено")
    from_wh = int(hdr["from_warehouse_id"])
    to_wh = int(hdr["to_warehouse_id"])

    rows = await connection.fetch(
        Select(
            TransferItem.id,
            TransferItem.material_id,
            TransferItem.quantity,
            TransferItem.new_batch_id,
        )
        .where(TransferItem.operation_id == operation_id)
        .order_by(TransferItem.id.asc())
    )
    for r in rows:
        if r["new_batch_id"] is not None:
            continue
        qty = r["quantity"]
        mat = int(r["material_id"])
        src = await find_fifo_batch_covering_quantity(connection, from_wh, mat, qty)
        if src is None:
            raise InsufficientStockError("Недостаточно одной партии на складе-отправителе под строку перемещения")
        old_id = int(src["id"])
        await adjust_batch_remaining(connection, old_id, -qty)
        new_id = await insert_inbound_batch(connection, warehouse_id=to_wh, material_id=mat, quantity=qty)
        await connection.execute(
            Update(TransferItem)
            .where(TransferItem.id == r["id"])
            .values(old_batch_id=old_id, new_batch_id=new_id)
        )


async def revert_transfer_completed(connection: Connection, operation_id: int) -> None:
    rows = await connection.fetch(
        Select(TransferItem.id, TransferItem.old_batch_id, TransferItem.new_batch_id, TransferItem.quantity)
        .where(
            TransferItem.operation_id == operation_id,
            TransferItem.new_batch_id.is_not(None),
        )
    )
    for r in rows:
        await adjust_batch_remaining(connection, int(r["old_batch_id"]), r["quantity"])
        await connection.execute(
            Update(TransferItem).where(TransferItem.id == r["id"]).values(old_batch_id=None, new_batch_id=None)
        )
        await connection.execute(Delete(Batch).where(Batch.id == int(r["new_batch_id"])))
