from datetime import UTC, datetime
from typing import Any

from asyncpg import Record
from everbase import Connection
from sqlalchemy import Delete, func, literal_column, Select, Update
from sqlalchemy.dialects.postgresql import Insert, aggregate_order_by

from core.models import Batch, Counterparty, Receipt, ReceiptItem, ReceiptStatus, StockOperation, StockOperationType, User

from modules.operations.exceptions import StockIntegrityError
from modules.operations.repositories import insert_inbound_batch
from modules.operations.receipt.schemes import ReceiptCreate, ReceiptUpdate


async def count_receipts(
    connection: Connection,
    user_id: int | None,
    created_from: datetime | None,
    created_to: datetime | None,
    status: ReceiptStatus | None,
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

    if status is not None:
        stmt = stmt.where(Receipt.status == status)

    return await connection.fetch_val(stmt, model=lambda x: int(x))


async def fetch_receipts(
    connection: Connection,
    page: int,
    limit: int,
    user_id: int | None,
    created_from: datetime | None,
    created_to: datetime | None,
    status: ReceiptStatus | None,
) -> list[Record]:
    rii = (
        Select(
            ReceiptItem.operation_id,
            func.json_agg(
                aggregate_order_by(
                    func.json_build_object(
                        "material_id",
                        ReceiptItem.material_id,
                        "quantity",
                        ReceiptItem.quantity,
                        "unit_price",
                        ReceiptItem.unit_price,
                        "batch_id",
                        ReceiptItem.batch_id,
                    ),
                    ReceiptItem.id.asc(),
                ),
            ).label("items_json"),
        )
        .group_by(ReceiptItem.operation_id)
    ).subquery("receipt_items_agg")
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
            User.name.label("created_by_user_name"),
            Counterparty.name.label("supplier_name"),
            StockOperation.created_at,
            StockOperation.completed_at,
            StockOperation.cancelled_at,
            func.coalesce(rii.c.items_json, literal_column("'[]'::json")).label("items"),
        )
        .select_from(Receipt)
        .join(StockOperation, StockOperation.id == Receipt.operation_id)
        .join(User, User.id == StockOperation.created_by_id)
        .join(Counterparty, Counterparty.id == Receipt.counterparty_id)
        .outerjoin(rii, rii.c.operation_id == StockOperation.id)
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

    if status is not None:
        stmt = stmt.where(Receipt.status == status)

    return await connection.fetch(stmt)


async def get_receipt(connection: Connection, operation_id: int) -> Record | None:
    rii = (
        Select(
            ReceiptItem.operation_id,
            func.json_agg(
                aggregate_order_by(
                    func.json_build_object(
                        "material_id",
                        ReceiptItem.material_id,
                        "quantity",
                        ReceiptItem.quantity,
                        "unit_price",
                        ReceiptItem.unit_price,
                        "batch_id",
                        ReceiptItem.batch_id,
                    ),
                    ReceiptItem.id.asc(),
                ),
            ).label("items_json"),
        )
        .group_by(ReceiptItem.operation_id)
    ).subquery("receipt_items_agg")
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
            User.name.label("created_by_user_name"),
            Counterparty.name.label("supplier_name"),
            StockOperation.created_at,
            StockOperation.completed_at,
            StockOperation.cancelled_at,
            func.coalesce(rii.c.items_json, literal_column("'[]'::json")).label("items"),
        )
        .select_from(Receipt)
        .join(StockOperation, StockOperation.id == Receipt.operation_id)
        .join(User, User.id == StockOperation.created_by_id)
        .join(Counterparty, Counterparty.id == Receipt.counterparty_id)
        .outerjoin(rii, rii.c.operation_id == StockOperation.id)
        .where(StockOperation.type == StockOperationType.RECEIPT, StockOperation.id == operation_id)
        .order_by(StockOperation.id.desc())
    )

    return await connection.fetch_row(stmt)


async def create_receipt(connection: Connection, user_id: int, payload: ReceiptCreate) -> int:
    now = datetime.now(UTC)
    so_extra: dict[str, Any] = {}
    if payload.status == ReceiptStatus.COMPLETED:
        so_extra["completed_at"] = now
    elif payload.status == ReceiptStatus.CANCELLED:
        so_extra["cancelled_at"] = now

    async with connection.transaction():
        op_id = await connection.fetch_val(
            Insert(StockOperation)
            .values(
                type=StockOperationType.RECEIPT,
                name=payload.name,
                performed_at=payload.performed_at,
                created_by_id=user_id,
                **so_extra,
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
                status=payload.status,
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

        if payload.status == ReceiptStatus.COMPLETED:
            await apply_receipt_completed(connection, int(op_id))

    return int(op_id)


async def update_receipt(connection: Connection, operation_id: int, payload: ReceiptUpdate) -> None:
    now = datetime.now(UTC)

    async with connection.transaction():
        prev = await connection.fetch_row(Select(Receipt.status).where(Receipt.operation_id == operation_id))
        if prev is None:
            return

        prev_status: ReceiptStatus = prev["status"]
        reverted_completed = False

        if payload.items is not None:
            if prev_status == ReceiptStatus.COMPLETED:
                await revert_receipt_completed(connection, operation_id)
                reverted_completed = True
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

        if payload.status is not None:
            if payload.status == ReceiptStatus.COMPLETED and (
                prev_status != ReceiptStatus.COMPLETED or reverted_completed
            ):
                await apply_receipt_completed(connection, operation_id)
            if (
                payload.status == ReceiptStatus.CANCELLED
                and prev_status == ReceiptStatus.COMPLETED
                and not reverted_completed
            ):
                await revert_receipt_completed(connection, operation_id)
        elif reverted_completed and prev_status == ReceiptStatus.COMPLETED:
            await apply_receipt_completed(connection, operation_id)

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


async def apply_receipt_completed(connection: Connection, operation_id: int) -> None:
    wh_rows = await connection.fetch_row(
        Select(Receipt.warehouse_id).where(Receipt.operation_id == operation_id)
    )
    if wh_rows is None:
        raise StockIntegrityError("Приёмка не найдена")
    warehouse_id = int(wh_rows["warehouse_id"])

    items = await connection.fetch(
        Select(ReceiptItem.id, ReceiptItem.material_id, ReceiptItem.quantity, ReceiptItem.batch_id)
        .where(ReceiptItem.operation_id == operation_id)
        .order_by(ReceiptItem.id.asc())
    )
    for it in items:
        if it["batch_id"] is not None:
            continue
        bid = await insert_inbound_batch(
            connection,
            warehouse_id=warehouse_id,
            material_id=int(it["material_id"]),
            quantity=it["quantity"],
        )
        await connection.execute(Update(ReceiptItem).where(ReceiptItem.id == it["id"]).values(batch_id=bid))


async def revert_receipt_completed(connection: Connection, operation_id: int) -> None:
    items = await connection.fetch(
        Select(ReceiptItem.id, ReceiptItem.batch_id)
        .where(ReceiptItem.operation_id == operation_id, ReceiptItem.batch_id.is_not(None))
    )
    for it in items:
        bid = int(it["batch_id"])
        await connection.execute(Update(ReceiptItem).where(ReceiptItem.id == it["id"]).values(batch_id=None))
        await connection.execute(Delete(Batch).where(Batch.id == bid))
