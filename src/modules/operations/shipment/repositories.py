from datetime import UTC, datetime
from typing import Any

from asyncpg import Record
from everbase import Connection
from sqlalchemy import Delete, literal_column, Select, Update, func
from sqlalchemy.dialects.postgresql import Insert, aggregate_order_by

from core.models import Counterparty, OperationStatus, Shipment, ShipmentItem, StockOperation, StockOperationType, User

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

        if payload.items is not None:
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
