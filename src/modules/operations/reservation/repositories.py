from datetime import datetime, UTC
from decimal import Decimal
from typing import Any

from asyncpg import Record
from everbase import Connection
from sqlalchemy import cast, func, Select, Update
from sqlalchemy.dialects.postgresql import Insert, JSON as PG_JSON

from core.models import Batch, Reservation, ReservationStatus, StockOperation, StockOperationType, User

from modules.operations.repositories import adjust_batch_remaining
from modules.operations.reservation.schemes import ReservationCreate, ReservationUpdate


async def count_reservations(
    connection: Connection,
    user_id: int | None,
    created_from: datetime | None,
    created_to: datetime | None,
    status: ReservationStatus | None,
) -> int:
    stmt = (
        Select(func.count())
        .select_from(Reservation)
        .join(StockOperation, StockOperation.id == Reservation.operation_id)
        .where(StockOperation.type == StockOperationType.RESERVATION)
    )

    if user_id is not None:
        stmt = stmt.where(StockOperation.created_by_id == user_id)

    if created_from is not None:
        stmt = stmt.where(StockOperation.created_at >= created_from)

    if created_to is not None:
        stmt = stmt.where(StockOperation.created_at <= created_to)

    if status is not None:
        stmt = stmt.where(Reservation.status == status)

    return await connection.fetch_val(stmt, model=lambda x: int(x))


async def fetch_reservations(
    connection: Connection,
    page: int,
    limit: int,
    user_id: int | None,
    created_from: datetime | None,
    created_to: datetime | None,
    status: ReservationStatus | None,
) -> list[Record]:
    stmt = (
        Select(
            StockOperation.id,
            StockOperation.name,
            StockOperation.performed_at,
            Reservation.status,
            Reservation.batch_id,
            Reservation.quantity,
            Batch.warehouse_id,
            cast(
                func.json_build_array(
                    func.json_build_object(
                        "material_id",
                        Batch.material_id,
                        "quantity",
                        Reservation.quantity,
                    ),
                ),
                PG_JSON,
            ).label("items"),
            StockOperation.created_by_id,
            User.name.label("created_by_user_name"),
            StockOperation.created_at,
            StockOperation.completed_at,
            StockOperation.cancelled_at,
        )
        .select_from(Reservation)
        .join(StockOperation, StockOperation.id == Reservation.operation_id)
        .join(User, User.id == StockOperation.created_by_id)
        .join(Batch, Batch.id == Reservation.batch_id)
        .where(StockOperation.type == StockOperationType.RESERVATION)
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
        stmt = stmt.where(Reservation.status == status)

    return await connection.fetch(stmt)


async def get_reservation(connection: Connection, operation_id: int) -> Record | None:
    stmt = (
        Select(
            StockOperation.id,
            StockOperation.name,
            StockOperation.performed_at,
            Reservation.status,
            Reservation.batch_id,
            Reservation.quantity,
            Batch.warehouse_id,
            cast(
                func.json_build_array(
                    func.json_build_object(
                        "material_id",
                        Batch.material_id,
                        "quantity",
                        Reservation.quantity,
                    ),
                ),
                PG_JSON,
            ).label("items"),
            StockOperation.created_by_id,
            User.name.label("created_by_user_name"),
            StockOperation.created_at,
            StockOperation.completed_at,
            StockOperation.cancelled_at,
        )
        .select_from(Reservation)
        .join(StockOperation, StockOperation.id == Reservation.operation_id)
        .join(User, User.id == StockOperation.created_by_id)
        .join(Batch, Batch.id == Reservation.batch_id)
        .where(StockOperation.type == StockOperationType.RESERVATION, StockOperation.id == operation_id)
        .order_by(StockOperation.id.desc())
    )

    return await connection.fetch_row(stmt)


async def create_reservation(connection: Connection, user_id: int, payload: ReservationCreate, fifo_batch_id: int) -> int:
    line = payload.items[0]
    perf = datetime.now(UTC)

    async with connection.transaction():
        op_id = await connection.fetch_val(
            Insert(StockOperation)
            .values(
                type=StockOperationType.RESERVATION,
                name=payload.name,
                performed_at=perf,
                created_by_id=user_id,
            )
            .returning(StockOperation.id)
        )

        await connection.execute(
            Insert(Reservation).values(
                operation_id=op_id,
                batch_id=fifo_batch_id,
                quantity=line.quantity,
                status=ReservationStatus.ACTIVE,
            )
        )

        await adjust_batch_remaining(connection, fifo_batch_id, -Decimal(str(line.quantity)))

    return int(op_id)


async def update_reservation(connection: Connection, operation_id: int, payload: ReservationUpdate) -> None:
    now = datetime.now(UTC)

    async with connection.transaction():
        prev = await connection.fetch_row(
            Select(Reservation.status, Reservation.batch_id, Reservation.quantity).where(
                Reservation.operation_id == operation_id
            )
        )
        if prev is None:
            return

        prev_status: ReservationStatus = prev["status"]

        if payload.status is not None:
            if payload.status == ReservationStatus.CANCELLED and prev_status == ReservationStatus.ACTIVE:
                await adjust_batch_remaining(
                    connection,
                    int(prev["batch_id"]),
                    Decimal(str(prev["quantity"])),
                )

        so_vals: dict[str, Any] = {}

        if payload.name is not None:
            so_vals["name"] = payload.name

        if payload.performed_at is not None:
            so_vals["performed_at"] = payload.performed_at

        if payload.status is not None:
            if payload.status == ReservationStatus.RELEASED:
                so_vals["completed_at"] = now
            elif payload.status == ReservationStatus.CANCELLED:
                so_vals["cancelled_at"] = now

        if so_vals:
            await connection.execute(Update(StockOperation).where(StockOperation.id == operation_id).values(**so_vals))

        r_vals: dict[str, Any] = {}

        if payload.quantity is not None:
            r_vals["quantity"] = payload.quantity

        if payload.status is not None:
            r_vals["status"] = payload.status

        if r_vals:
            await connection.execute(
                Update(Reservation).where(Reservation.operation_id == operation_id).values(**r_vals)
            )
