from datetime import UTC, datetime
from typing import Any

from asyncpg import Record
from everbase import Connection
from sqlalchemy import Delete, func, Select, Update
from sqlalchemy.dialects.postgresql import Insert

from core.models import Receipt, ReceiptItem, ReceiptStatus, StockOperation, StockOperationType

from modules.operations.receipt.schemes import ReceiptCreate, ReceiptUpdate


async def count_receipts(
    connection: Connection,
    user_id: int | None,
    created_from: datetime | None,
    created_to: datetime | None,
) -> int:
    stmt = (
        Select(func.count())
        .select_from(Receipt)
        .join(StockOperation, StockOperation.id == Receipt.operation_id)
        .where(StockOperation.type == StockOperationType.RECEIPT)
    )

    if user_id is not None:
        stmt = stmt.where(StockOperation.created_by_id == user_id)

    if created_from is not None:
        stmt = stmt.where(StockOperation.created_at >= created_from)

    if created_to is not None:
        stmt = stmt.where(StockOperation.created_at <= created_to)

    return await connection.fetch_val(stmt, model=lambda x: int(x))


async def fetch_receipts(
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
            Receipt.status,
            Receipt.counterparty_id,
            Receipt.warehouse_id,
            Receipt.shipping_price,
            Receipt.discount,
            StockOperation.created_by_id,
            StockOperation.created_at,
            StockOperation.completed_at,
            StockOperation.cancelled_at,
        )
        .select_from(Receipt)
        .join(StockOperation, StockOperation.id == Receipt.operation_id)
        .where(StockOperation.type == StockOperationType.RECEIPT)
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


async def get_receipt(connection: Connection, operation_id: int) -> Record | None:
    stmt = (
        Select(
            StockOperation.id,
            StockOperation.name,
            StockOperation.performed_at,
            Receipt.status,
            Receipt.counterparty_id,
            Receipt.warehouse_id,
            Receipt.shipping_price,
            Receipt.discount,
            StockOperation.created_by_id,
            StockOperation.created_at,
            StockOperation.completed_at,
            StockOperation.cancelled_at,
        )
        .select_from(Receipt)
        .join(StockOperation, StockOperation.id == Receipt.operation_id)
        .where(StockOperation.type == StockOperationType.RECEIPT, StockOperation.id == operation_id)
        .order_by(StockOperation.id.desc())
    )

    return await connection.fetch_row(stmt)


async def create_receipt(connection: Connection, user_id: int, payload: ReceiptCreate) -> int:
    async with connection.transaction():
        op_id = await connection.fetch_val(
            Insert(StockOperation)
            .values(
                type=StockOperationType.RECEIPT,
                name=payload.name,
                performed_at=payload.performed_at,
                created_by_id=user_id,
            )
            .returning(StockOperation.id)
        )

        await connection.execute(
            Insert(Receipt).values(
                operation_id=op_id,
                counterparty_id=payload.supplier_id,
                warehouse_id=payload.warehouse_id,
                shipping_price=payload.shipping_price,
                discount=payload.discount,
                status=ReceiptStatus.DRAFT,
            )
        )

        for it in payload.items:
            await connection.execute(
                Insert(ReceiptItem).values(
                    operation_id=op_id,
                    material_id=it.material_id,
                    quantity=it.quantity,
                    unit_price=it.unit_price,
                    batch_id=None,
                )
            )

    return int(op_id)


async def update_receipt(connection: Connection, operation_id: int, payload: ReceiptUpdate) -> None:
    now = datetime.now(UTC)

    async with connection.transaction():
        so_vals: dict[str, Any] = {}

        if payload.name is not None:
            so_vals["name"] = payload.name

        if payload.performed_at is not None:
            so_vals["performed_at"] = payload.performed_at

        if payload.status is not None:
            if payload.status == ReceiptStatus.COMPLETED:
                so_vals["completed_at"] = now
            elif payload.status == ReceiptStatus.CANCELLED:
                so_vals["cancelled_at"] = now

        if so_vals:
            await connection.execute(Update(StockOperation).where(StockOperation.id == operation_id).values(**so_vals))

        r_vals: dict[str, Any] = {}

        if payload.warehouse_id is not None:
            r_vals["warehouse_id"] = payload.warehouse_id

        if payload.supplier_id is not None:
            r_vals["counterparty_id"] = payload.supplier_id

        if payload.shipping_price is not None:
            r_vals["shipping_price"] = payload.shipping_price

        if payload.discount is not None:
            r_vals["discount"] = payload.discount

        if payload.status is not None:
            r_vals["status"] = payload.status

        if r_vals:
            await connection.execute(Update(Receipt).where(Receipt.operation_id == operation_id).values(**r_vals))

        if payload.items is not None:
            await connection.execute(Delete(ReceiptItem).where(ReceiptItem.operation_id == operation_id))

            for it in payload.items:
                await connection.execute(
                    Insert(ReceiptItem).values(
                        operation_id=operation_id,
                        material_id=it.material_id,
                        quantity=it.quantity,
                        unit_price=it.unit_price,
                        batch_id=None,
                    )
                )
