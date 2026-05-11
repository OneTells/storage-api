from datetime import UTC, datetime
from typing import Any

from asyncpg import Record
from everbase import Connection
from sqlalchemy import Delete, Select, Update, func
from sqlalchemy.dialects.postgresql import Insert

from core.models import OperationStatus, StockOperation, StockOperationType, Transfer, TransferItem

from modules.operations.transfer.schemes import TransferCreate, TransferUpdate


async def count_transfers(
    connection: Connection,
    user_id: int | None,
    created_from: datetime | None,
    created_to: datetime | None,
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

    return await connection.fetch_val(stmt, model=lambda x: int(x))


async def fetch_transfers(
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
            Transfer.status,
            Transfer.from_warehouse_id,
            Transfer.to_warehouse_id,
            StockOperation.created_by_id,
            StockOperation.created_at,
            StockOperation.completed_at,
            StockOperation.cancelled_at,
        )
        .select_from(Transfer)
        .join(StockOperation, StockOperation.id == Transfer.operation_id)
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

    return await connection.fetch(stmt)


async def get_transfer(connection: Connection, operation_id: int) -> Record | None:
    stmt = (
        Select(
            StockOperation.id,
            StockOperation.name,
            StockOperation.performed_at,
            Transfer.status,
            Transfer.from_warehouse_id,
            Transfer.to_warehouse_id,
            StockOperation.created_by_id,
            StockOperation.created_at,
            StockOperation.completed_at,
            StockOperation.cancelled_at,
        )
        .select_from(Transfer)
        .join(StockOperation, StockOperation.id == Transfer.operation_id)
        .where(StockOperation.type == StockOperationType.TRANSFER, StockOperation.id == operation_id)
        .order_by(StockOperation.id.desc())
    )

    return await connection.fetch_row(stmt)


async def create_transfer(connection: Connection, user_id: int, payload: TransferCreate) -> int:
    async with connection.transaction():
        op_id = await connection.fetch_val(
            Insert(StockOperation)
            .values(
                type=StockOperationType.TRANSFER,
                name=payload.name,
                performed_at=payload.performed_at,
                created_by_id=user_id,
            )
            .returning(StockOperation.id)
        )

        await connection.execute(
            Insert(Transfer).values(
                operation_id=op_id,
                from_warehouse_id=payload.from_warehouse_id,
                to_warehouse_id=payload.to_warehouse_id,
                status=OperationStatus.DRAFT,
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

    return int(op_id)


async def update_transfer(connection: Connection, operation_id: int, payload: TransferUpdate) -> None:
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

        t_vals: dict[str, Any] = {}

        if payload.from_warehouse_id is not None:
            t_vals["from_warehouse_id"] = payload.from_warehouse_id

        if payload.to_warehouse_id is not None:
            t_vals["to_warehouse_id"] = payload.to_warehouse_id

        if payload.status is not None:
            t_vals["status"] = payload.status

        if t_vals:
            await connection.execute(Update(Transfer).where(Transfer.operation_id == operation_id).values(**t_vals))

        if payload.items is not None:
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
