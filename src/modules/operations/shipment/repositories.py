from datetime import UTC, datetime
from typing import Any

from asyncpg import Record
from everbase import Connection
from sqlalchemy import Delete, literal_column, Select, Update, func
from sqlalchemy.dialects.postgresql import Insert, aggregate_order_by

from core.models import Counterparty, OperationStatus, Shipment, ShipmentItem, StockOperation, StockOperationType, User

from modules.operations.exceptions import InsufficientStockError, StockIntegrityError
from modules.operations.repositories import adjust_batch_remaining, try_single_batch_outbound
from modules.operations.shipment.schemes import ShipmentCreate, ShipmentUpdate


async def count_shipments(
    connection: Connection,
    user_id: int | None,
    created_from: datetime | None,
    created_to: datetime | None,
    status: OperationStatus | None,
) -> int:
    stmt = (
        Select(func.count())
        .select_from(Shipment)
        .join(StockOperation, StockOperation.id == Shipment.operation_id)
        .where(StockOperation.type == StockOperationType.SHIPMENT)
    )

    if user_id is not None:
        stmt = stmt.where(StockOperation.created_by_id == user_id)

    if created_from is not None:
        stmt = stmt.where(StockOperation.created_at >= created_from)

    if created_to is not None:
        stmt = stmt.where(StockOperation.created_at <= created_to)

    if status is not None:
        stmt = stmt.where(Shipment.status == status)

    return await connection.fetch_val(stmt, model=lambda x: int(x))


async def fetch_shipments(
    connection: Connection,
    page: int,
    limit: int,
    user_id: int | None,
    created_from: datetime | None,
    created_to: datetime | None,
    status: OperationStatus | None,
) -> list[Record]:
    sqi = (
        Select(
            ShipmentItem.operation_id,
            func.json_agg(
                aggregate_order_by(
                    func.json_build_object(
                        "material_id",
                        ShipmentItem.material_id,
                        "quantity",
                        ShipmentItem.quantity,
                        "batch_id",
                        ShipmentItem.batch_id,
                    ),
                    ShipmentItem.id.asc(),
                ),
            ).label("items_json"),
        )
        .group_by(ShipmentItem.operation_id)
    ).subquery("shipment_items_agg")
    stmt = (
        Select(
            StockOperation.id,
            StockOperation.name,
            StockOperation.performed_at,
            Shipment.status,
            Shipment.counterparty_id,
            Shipment.warehouse_id,
            Shipment.order_number,
            StockOperation.created_by_id,
            User.name.label("created_by_user_name"),
            Counterparty.name.label("customer_name"),
            StockOperation.created_at,
            StockOperation.completed_at,
            StockOperation.cancelled_at,
            func.coalesce(sqi.c.items_json, literal_column("'[]'::json")).label("items"),
        )
        .select_from(Shipment)
        .join(StockOperation, StockOperation.id == Shipment.operation_id)
        .join(User, User.id == StockOperation.created_by_id)
        .join(Counterparty, Counterparty.id == Shipment.counterparty_id)
        .outerjoin(sqi, sqi.c.operation_id == StockOperation.id)
        .where(StockOperation.type == StockOperationType.SHIPMENT)
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
        stmt = stmt.where(Shipment.status == status)

    return await connection.fetch(stmt)


async def get_shipment(connection: Connection, operation_id: int) -> Record | None:
    sqi = (
        Select(
            ShipmentItem.operation_id,
            func.json_agg(
                aggregate_order_by(
                    func.json_build_object(
                        "material_id",
                        ShipmentItem.material_id,
                        "quantity",
                        ShipmentItem.quantity,
                        "batch_id",
                        ShipmentItem.batch_id,
                    ),
                    ShipmentItem.id.asc(),
                ),
            ).label("items_json"),
        )
        .group_by(ShipmentItem.operation_id)
    ).subquery("shipment_items_agg")
    stmt = (
        Select(
            StockOperation.id,
            StockOperation.name,
            StockOperation.performed_at,
            Shipment.status,
            Shipment.counterparty_id,
            Shipment.warehouse_id,
            Shipment.order_number,
            StockOperation.created_by_id,
            User.name.label("created_by_user_name"),
            Counterparty.name.label("customer_name"),
            StockOperation.created_at,
            StockOperation.completed_at,
            StockOperation.cancelled_at,
            func.coalesce(sqi.c.items_json, literal_column("'[]'::json")).label("items"),
        )
        .select_from(Shipment)
        .join(StockOperation, StockOperation.id == Shipment.operation_id)
        .join(User, User.id == StockOperation.created_by_id)
        .join(Counterparty, Counterparty.id == Shipment.counterparty_id)
        .outerjoin(sqi, sqi.c.operation_id == StockOperation.id)
        .where(StockOperation.type == StockOperationType.SHIPMENT, StockOperation.id == operation_id)
        .order_by(StockOperation.id.desc())
    )

    return await connection.fetch_row(stmt)


async def create_shipment(connection: Connection, user_id: int, payload: ShipmentCreate) -> int:
    async with connection.transaction():
        op_id = await connection.fetch_val(
            Insert(StockOperation)
            .values(
                type=StockOperationType.SHIPMENT,
                name=payload.name,
                performed_at=payload.performed_at,
                created_by_id=user_id,
            )
            .returning(StockOperation.id)
        )

        await connection.execute(
            Insert(Shipment).values(
                operation_id=op_id,
                counterparty_id=payload.customer_id,
                warehouse_id=payload.warehouse_id,
                order_number=payload.order_number,
                status=OperationStatus.DRAFT,
            )
        )

        for it in payload.items:
            await connection.execute(
                Insert(ShipmentItem).values(
                    operation_id=op_id,
                    material_id=it.material_id,
                    quantity=it.quantity,
                    batch_id=None,
                )
            )

    return int(op_id)


async def update_shipment(connection: Connection, operation_id: int, payload: ShipmentUpdate) -> None:
    now = datetime.now(UTC)

    async with connection.transaction():
        prev = await connection.fetch_row(Select(Shipment.status).where(Shipment.operation_id == operation_id))
        if prev is None:
            return

        prev_status: OperationStatus = prev["status"]
        reverted_completed = False

        if payload.items is not None:
            if prev_status == OperationStatus.COMPLETED:
                await revert_shipment_completed(connection, operation_id)
                reverted_completed = True
            await connection.execute(Delete(ShipmentItem).where(ShipmentItem.operation_id == operation_id))

            for it in payload.items:
                await connection.execute(
                    Insert(ShipmentItem).values(
                        operation_id=operation_id,
                        material_id=it.material_id,
                        quantity=it.quantity,
                        batch_id=None,
                    )
                )

        if payload.status is not None:
            if payload.status == OperationStatus.COMPLETED and (
                prev_status != OperationStatus.COMPLETED or reverted_completed
            ):
                await apply_shipment_completed(connection, operation_id)
            if (
                payload.status == OperationStatus.CANCELLED
                and prev_status == OperationStatus.COMPLETED
                and not reverted_completed
            ):
                await revert_shipment_completed(connection, operation_id)
        elif reverted_completed and prev_status == OperationStatus.COMPLETED:
            await apply_shipment_completed(connection, operation_id)

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

        s_vals: dict[str, Any] = {}

        if payload.warehouse_id is not None:
            s_vals["warehouse_id"] = payload.warehouse_id

        if payload.customer_id is not None:
            s_vals["counterparty_id"] = payload.customer_id

        if payload.order_number is not None:
            s_vals["order_number"] = payload.order_number

        if payload.status is not None:
            s_vals["status"] = payload.status

        if s_vals:
            await connection.execute(Update(Shipment).where(Shipment.operation_id == operation_id).values(**s_vals))


async def apply_shipment_completed(connection: Connection, operation_id: int) -> None:
    hdr = await connection.fetch_row(
        Select(Shipment.warehouse_id).where(Shipment.operation_id == operation_id)
    )
    if hdr is None:
        raise StockIntegrityError("Отгрузка не найдена")
    wh = int(hdr["warehouse_id"])

    rows = await connection.fetch(
        Select(ShipmentItem.id, ShipmentItem.material_id, ShipmentItem.quantity, ShipmentItem.batch_id)
        .where(ShipmentItem.operation_id == operation_id)
        .order_by(ShipmentItem.id.asc())
    )
    for r in rows:
        if r["batch_id"] is not None:
            continue
        bid = await try_single_batch_outbound(
            connection, warehouse_id=wh, material_id=int(r["material_id"]), quantity=r["quantity"]
        )
        if bid is None:
            raise InsufficientStockError(
                "Недостаточно одной партии с полным остатком под строку отгрузки (увеличьте срок партий или разбейте строку)"
            )
        await connection.execute(Update(ShipmentItem).where(ShipmentItem.id == r["id"]).values(batch_id=bid))


async def revert_shipment_completed(connection: Connection, operation_id: int) -> None:
    rows = await connection.fetch(
        Select(ShipmentItem.batch_id, ShipmentItem.quantity)
        .where(ShipmentItem.operation_id == operation_id, ShipmentItem.batch_id.is_not(None))
    )
    for r in rows:
        await adjust_batch_remaining(connection, int(r["batch_id"]), r["quantity"])
    await connection.execute(
        Update(ShipmentItem).where(ShipmentItem.operation_id == operation_id).values(batch_id=None)
    )
