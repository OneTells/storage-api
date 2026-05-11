from datetime import UTC, datetime
from typing import Any

from asyncpg import Record
from everbase import Connection
from sqlalchemy import Delete, Select, Update, func
from sqlalchemy.dialects.postgresql import Insert

from core.models import OperationStatus, StockOperation, StockOperationType, WriteOffToProduction, WriteOffToProductionItem

from modules.operations.write_off_to_production.schemes import WriteOffToProductionCreate, WriteOffToProductionUpdate


async def count_write_offs_to_production(
    connection: Connection,
    user_id: int | None,
    created_from: datetime | None,
    created_to: datetime | None,
) -> int:
    stmt = (
        Select(func.count())
        .select_from(WriteOffToProduction)
        .join(StockOperation, StockOperation.id == WriteOffToProduction.operation_id)
        .where(StockOperation.type == StockOperationType.WRITE_OFF_TO_PRODUCTION)
    )

    if user_id is not None:
        stmt = stmt.where(StockOperation.created_by_id == user_id)

    if created_from is not None:
        stmt = stmt.where(StockOperation.created_at >= created_from)

    if created_to is not None:
        stmt = stmt.where(StockOperation.created_at <= created_to)

    return await connection.fetch_val(stmt, model=lambda x: int(x))


async def fetch_write_offs_to_production(
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
            WriteOffToProduction.status,
            WriteOffToProduction.warehouse_id,
            WriteOffToProduction.production_order_id.label("production_order_reference"),
            StockOperation.created_by_id,
            StockOperation.created_at,
            StockOperation.completed_at,
            StockOperation.cancelled_at,
        )
        .select_from(WriteOffToProduction)
        .join(StockOperation, StockOperation.id == WriteOffToProduction.operation_id)
        .where(StockOperation.type == StockOperationType.WRITE_OFF_TO_PRODUCTION)
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


async def get_write_off_to_production(connection: Connection, operation_id: int) -> Record | None:
    stmt = (
        Select(
            StockOperation.id,
            StockOperation.name,
            StockOperation.performed_at,
            WriteOffToProduction.status,
            WriteOffToProduction.warehouse_id,
            WriteOffToProduction.production_order_id.label("production_order_reference"),
            StockOperation.created_by_id,
            StockOperation.created_at,
            StockOperation.completed_at,
            StockOperation.cancelled_at,
        )
        .select_from(WriteOffToProduction)
        .join(StockOperation, StockOperation.id == WriteOffToProduction.operation_id)
        .where(StockOperation.type == StockOperationType.WRITE_OFF_TO_PRODUCTION, StockOperation.id == operation_id)
        .order_by(StockOperation.id.desc())
    )

    return await connection.fetch_row(stmt)


async def create_write_off_to_production(connection: Connection, user_id: int, payload: WriteOffToProductionCreate) -> int:
    async with connection.transaction():
        op_id = await connection.fetch_val(
            Insert(StockOperation)
            .values(
                type=StockOperationType.WRITE_OFF_TO_PRODUCTION,
                name=payload.name,
                performed_at=payload.performed_at,
                created_by_id=user_id,
            )
            .returning(StockOperation.id)
        )

        await connection.execute(
            Insert(WriteOffToProduction).values(
                operation_id=op_id,
                warehouse_id=payload.warehouse_id,
                production_order_id=payload.production_order_reference,
                status=OperationStatus.DRAFT,
            )
        )

        for it in payload.items:
            await connection.execute(
                Insert(WriteOffToProductionItem).values(
                    operation_id=op_id,
                    material_id=it.material_id,
                    quantity=it.quantity,
                    unit_price=it.unit_price,
                    batch_id=None,
                )
            )

    return int(op_id)


async def update_write_off_to_production(
    connection: Connection, operation_id: int, payload: WriteOffToProductionUpdate
) -> None:
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

        if payload.production_order_reference is not None:
            w_vals["production_order_id"] = payload.production_order_reference

        if payload.status is not None:
            w_vals["status"] = payload.status

        if w_vals:
            await connection.execute(
                Update(WriteOffToProduction).where(WriteOffToProduction.operation_id == operation_id).values(**w_vals)
            )

        if payload.items is not None:
            await connection.execute(
                Delete(WriteOffToProductionItem).where(WriteOffToProductionItem.operation_id == operation_id)
            )

            for it in payload.items:
                await connection.execute(
                    Insert(WriteOffToProductionItem).values(
                        operation_id=operation_id,
                        material_id=it.material_id,
                        quantity=it.quantity,
                        unit_price=it.unit_price,
                        batch_id=None,
                    )
                )
