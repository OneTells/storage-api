from datetime import UTC, datetime
from typing import Any

from asyncpg import Record
from everbase import Connection
from sqlalchemy import Delete, literal_column, Select, Update, func
from sqlalchemy.dialects.postgresql import Insert, aggregate_order_by

from core.models import (
    OperationStatus,
    StockOperation,
    StockOperationType,
    User,
    WriteOffToProduction,
    WriteOffToProductionItem,
)

from modules.operations.exceptions import InsufficientStockError, StockIntegrityError
from modules.operations.repositories import adjust_batch_remaining, try_single_batch_outbound
from modules.operations.write_off_to_production.schemes import WriteOffToProductionCreate, WriteOffToProductionUpdate


async def count_write_offs_to_production(
    connection: Connection,
    user_id: int | None,
    created_from: datetime | None,
    created_to: datetime | None,
    status: OperationStatus | None,
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

    if status is not None:
        stmt = stmt.where(WriteOffToProduction.status == status)

    return await connection.fetch_val(stmt, model=lambda x: int(x))


async def fetch_write_offs_to_production(
    connection: Connection,
    page: int,
    limit: int,
    user_id: int | None,
    created_from: datetime | None,
    created_to: datetime | None,
    status: OperationStatus | None,
) -> list[Record]:
    wti = (
        Select(
            WriteOffToProductionItem.operation_id,
            func.json_agg(
                aggregate_order_by(
                    func.json_build_object(
                        "material_id",
                        WriteOffToProductionItem.material_id,
                        "quantity",
                        WriteOffToProductionItem.quantity,
                        "unit_price",
                        WriteOffToProductionItem.unit_price,
                        "batch_id",
                        WriteOffToProductionItem.batch_id,
                    ),
                    WriteOffToProductionItem.id.asc(),
                ),
            ).label("items_json"),
        )
        .group_by(WriteOffToProductionItem.operation_id)
    ).subquery("write_off_tp_items_agg")
    stmt = (
        Select(
            StockOperation.id,
            StockOperation.name,
            StockOperation.performed_at,
            WriteOffToProduction.status,
            WriteOffToProduction.warehouse_id,
            WriteOffToProduction.production_order_id.label("production_order_reference"),
            StockOperation.created_by_id,
            User.name.label("created_by_user_name"),
            StockOperation.created_at,
            StockOperation.completed_at,
            StockOperation.cancelled_at,
            func.coalesce(wti.c.items_json, literal_column("'[]'::json")).label("items"),
        )
        .select_from(WriteOffToProduction)
        .join(StockOperation, StockOperation.id == WriteOffToProduction.operation_id)
        .join(User, User.id == StockOperation.created_by_id)
        .outerjoin(wti, wti.c.operation_id == StockOperation.id)
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

    if status is not None:
        stmt = stmt.where(WriteOffToProduction.status == status)

    return await connection.fetch(stmt)


async def get_write_off_to_production(connection: Connection, operation_id: int) -> Record | None:
    wti = (
        Select(
            WriteOffToProductionItem.operation_id,
            func.json_agg(
                aggregate_order_by(
                    func.json_build_object(
                        "material_id",
                        WriteOffToProductionItem.material_id,
                        "quantity",
                        WriteOffToProductionItem.quantity,
                        "unit_price",
                        WriteOffToProductionItem.unit_price,
                        "batch_id",
                        WriteOffToProductionItem.batch_id,
                    ),
                    WriteOffToProductionItem.id.asc(),
                ),
            ).label("items_json"),
        )
        .group_by(WriteOffToProductionItem.operation_id)
    ).subquery("write_off_tp_items_agg")
    stmt = (
        Select(
            StockOperation.id,
            StockOperation.name,
            StockOperation.performed_at,
            WriteOffToProduction.status,
            WriteOffToProduction.warehouse_id,
            WriteOffToProduction.production_order_id.label("production_order_reference"),
            StockOperation.created_by_id,
            User.name.label("created_by_user_name"),
            StockOperation.created_at,
            StockOperation.completed_at,
            StockOperation.cancelled_at,
            func.coalesce(wti.c.items_json, literal_column("'[]'::json")).label("items"),
        )
        .select_from(WriteOffToProduction)
        .join(StockOperation, StockOperation.id == WriteOffToProduction.operation_id)
        .join(User, User.id == StockOperation.created_by_id)
        .outerjoin(wti, wti.c.operation_id == StockOperation.id)
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
        prev = await connection.fetch_row(
            Select(WriteOffToProduction.status).where(WriteOffToProduction.operation_id == operation_id)
        )
        if prev is None:
            return

        prev_status: OperationStatus = prev["status"]
        reverted_completed = False

        if payload.items is not None:
            if prev_status == OperationStatus.COMPLETED:
                await revert_write_off_to_production_completed(connection, operation_id)
                reverted_completed = True
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

        if payload.status is not None:
            if payload.status == OperationStatus.COMPLETED and (
                prev_status != OperationStatus.COMPLETED or reverted_completed
            ):
                await apply_write_off_to_production_completed(connection, operation_id)
            if (
                payload.status == OperationStatus.CANCELLED
                and prev_status == OperationStatus.COMPLETED
                and not reverted_completed
            ):
                await revert_write_off_to_production_completed(connection, operation_id)
        elif reverted_completed and prev_status == OperationStatus.COMPLETED:
            await apply_write_off_to_production_completed(connection, operation_id)

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


async def apply_write_off_to_production_completed(connection: Connection, operation_id: int) -> None:
    hdr = await connection.fetch_row(
        Select(WriteOffToProduction.warehouse_id).where(WriteOffToProduction.operation_id == operation_id)
    )
    if hdr is None:
        raise StockIntegrityError("Списание в производство не найдено")
    wh = int(hdr["warehouse_id"])

    rows = await connection.fetch(
        Select(
            WriteOffToProductionItem.id,
            WriteOffToProductionItem.material_id,
            WriteOffToProductionItem.quantity,
            WriteOffToProductionItem.batch_id,
        )
        .where(WriteOffToProductionItem.operation_id == operation_id)
        .order_by(WriteOffToProductionItem.id.asc())
    )
    for r in rows:
        if r["batch_id"] is not None:
            continue
        bid = await try_single_batch_outbound(
            connection, warehouse_id=wh, material_id=int(r["material_id"]), quantity=r["quantity"]
        )
        if bid is None:
            raise InsufficientStockError("Недостаточно одной партии под строку списания в производство")
        await connection.execute(
            Update(WriteOffToProductionItem).where(WriteOffToProductionItem.id == r["id"]).values(batch_id=bid)
        )


async def revert_write_off_to_production_completed(connection: Connection, operation_id: int) -> None:
    rows = await connection.fetch(
        Select(WriteOffToProductionItem.batch_id, WriteOffToProductionItem.quantity)
        .where(
            WriteOffToProductionItem.operation_id == operation_id,
            WriteOffToProductionItem.batch_id.is_not(None),
        )
    )
    for r in rows:
        await adjust_batch_remaining(connection, int(r["batch_id"]), r["quantity"])
    await connection.execute(
        Update(WriteOffToProductionItem)
        .where(WriteOffToProductionItem.operation_id == operation_id)
        .values(batch_id=None)
    )
