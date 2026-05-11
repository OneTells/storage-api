from datetime import UTC, datetime
from typing import Any

from asyncpg import Record
from everbase import Connection
from sqlalchemy import Delete, literal_column, Select, Update, func
from sqlalchemy.dialects.postgresql import Insert, aggregate_order_by

from core.models import OperationStatus, StockOperation, StockOperationType, User, WriteOff, WriteOffItem

from modules.operations.write_off.schemes import WriteOffCreate, WriteOffUpdate


async def count_write_offs(
    connection: Connection,
    user_id: int | None,
    created_from: datetime | None,
    created_to: datetime | None,
    status: OperationStatus | None,
) -> int:
    stmt = (
        Select(func.count())
        .select_from(WriteOff)
        .join(StockOperation, StockOperation.id == WriteOff.operation_id)
        .where(StockOperation.type == StockOperationType.WRITE_OFF)
    )

    if user_id is not None:
        stmt = stmt.where(StockOperation.created_by_id == user_id)

    if created_from is not None:
        stmt = stmt.where(StockOperation.created_at >= created_from)

    if created_to is not None:
        stmt = stmt.where(StockOperation.created_at <= created_to)

    if status is not None:
        stmt = stmt.where(WriteOff.status == status)

    return await connection.fetch_val(stmt, model=lambda x: int(x))


async def fetch_write_offs(
    connection: Connection,
    page: int,
    limit: int,
    user_id: int | None,
    created_from: datetime | None,
    created_to: datetime | None,
    status: OperationStatus | None,
) -> list[Record]:
    woi = (
        Select(
            WriteOffItem.operation_id,
            func.json_agg(
                aggregate_order_by(
                    func.json_build_object(
                        "material_id",
                        WriteOffItem.material_id,
                        "quantity",
                        WriteOffItem.quantity,
                        "reason",
                        WriteOffItem.reason,
                        "batch_id",
                        WriteOffItem.batch_id,
                    ),
                    WriteOffItem.id.asc(),
                ),
            ).label("items_json"),
        )
        .group_by(WriteOffItem.operation_id)
    ).subquery("write_off_items_agg")
    stmt = (
        Select(
            StockOperation.id,
            StockOperation.name,
            StockOperation.performed_at,
            WriteOff.status,
            WriteOff.warehouse_id,
            WriteOff.reason,
            StockOperation.created_by_id,
            User.name.label("created_by_user_name"),
            StockOperation.created_at,
            StockOperation.completed_at,
            StockOperation.cancelled_at,
            func.coalesce(woi.c.items_json, literal_column("'[]'::json")).label("items"),
        )
        .select_from(WriteOff)
        .join(StockOperation, StockOperation.id == WriteOff.operation_id)
        .join(User, User.id == StockOperation.created_by_id)
        .outerjoin(woi, woi.c.operation_id == StockOperation.id)
        .where(StockOperation.type == StockOperationType.WRITE_OFF)
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
        stmt = stmt.where(WriteOff.status == status)

    return await connection.fetch(stmt)


async def get_write_off(connection: Connection, operation_id: int) -> Record | None:
    woi = (
        Select(
            WriteOffItem.operation_id,
            func.json_agg(
                aggregate_order_by(
                    func.json_build_object(
                        "material_id",
                        WriteOffItem.material_id,
                        "quantity",
                        WriteOffItem.quantity,
                        "reason",
                        WriteOffItem.reason,
                        "batch_id",
                        WriteOffItem.batch_id,
                    ),
                    WriteOffItem.id.asc(),
                ),
            ).label("items_json"),
        )
        .group_by(WriteOffItem.operation_id)
    ).subquery("write_off_items_agg")
    stmt = (
        Select(
            StockOperation.id,
            StockOperation.name,
            StockOperation.performed_at,
            WriteOff.status,
            WriteOff.warehouse_id,
            WriteOff.reason,
            StockOperation.created_by_id,
            User.name.label("created_by_user_name"),
            StockOperation.created_at,
            StockOperation.completed_at,
            StockOperation.cancelled_at,
            func.coalesce(woi.c.items_json, literal_column("'[]'::json")).label("items"),
        )
        .select_from(WriteOff)
        .join(StockOperation, StockOperation.id == WriteOff.operation_id)
        .join(User, User.id == StockOperation.created_by_id)
        .outerjoin(woi, woi.c.operation_id == StockOperation.id)
        .where(StockOperation.type == StockOperationType.WRITE_OFF, StockOperation.id == operation_id)
        .order_by(StockOperation.id.desc())
    )

    return await connection.fetch_row(stmt)


async def create_write_off(connection: Connection, user_id: int, payload: WriteOffCreate) -> int:
    async with connection.transaction():
        op_id = await connection.fetch_val(
            Insert(StockOperation)
            .values(
                type=StockOperationType.WRITE_OFF,
                name=payload.name,
                performed_at=payload.performed_at,
                created_by_id=user_id,
            )
            .returning(StockOperation.id)
        )

        await connection.execute(
            Insert(WriteOff).values(
                operation_id=op_id,
                warehouse_id=payload.warehouse_id,
                reason=payload.reason,
                status=OperationStatus.DRAFT,
            )
        )

        for it in payload.items:
            await connection.execute(
                Insert(WriteOffItem).values(
                    operation_id=op_id,
                    material_id=it.material_id,
                    quantity=it.quantity,
                    reason=it.reason,
                    batch_id=None,
                )
            )

    return int(op_id)


async def update_write_off(connection: Connection, operation_id: int, payload: WriteOffUpdate) -> None:
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

        w_vals: dict[str, Any] = {}

        if payload.warehouse_id is not None:
            w_vals["warehouse_id"] = payload.warehouse_id

        if payload.reason is not None:
            w_vals["reason"] = payload.reason

        if payload.status is not None:
            w_vals["status"] = payload.status

        if w_vals:
            await connection.execute(Update(WriteOff).where(WriteOff.operation_id == operation_id).values(**w_vals))

        if payload.items is not None:
            await connection.execute(Delete(WriteOffItem).where(WriteOffItem.operation_id == operation_id))

            for it in payload.items:
                await connection.execute(
                    Insert(WriteOffItem).values(
                        operation_id=operation_id,
                        material_id=it.material_id,
                        quantity=it.quantity,
                        reason=it.reason,
                        batch_id=None,
                    )
                )
