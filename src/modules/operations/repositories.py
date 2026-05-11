from decimal import Decimal

from asyncpg import Record
from everbase import Connection
from sqlalchemy import Select

from core.models import Batch, Counterparty, CounterpartyRoleType, Material, ProductionOrder, Warehouse


async def warehouse_exists(connection: Connection, warehouse_id: int) -> bool:
    query = Select(
        Select(1)
        .select_from(Warehouse)
        .where(Warehouse.id == warehouse_id)
        .exists()
    )

    return bool(await connection.fetch_val(query))


async def material_exists(connection: Connection, material_id: int) -> bool:
    query = Select(
        Select(1)
        .select_from(Material)
        .where(Material.id == material_id)
        .exists()
    )

    return bool(await connection.fetch_val(query))


async def production_order_exists(connection: Connection, order_id: int) -> bool:
    query = Select(
        Select(1)
        .select_from(ProductionOrder)
        .where(ProductionOrder.id == order_id)
        .exists()
    )

    return bool(await connection.fetch_val(query))


async def counterparty_role_exists(connection: Connection, counterparty_id: int, role: CounterpartyRoleType) -> bool:
    query = Select(
        Select(1)
        .select_from(Counterparty)
        .where(
            Counterparty.id == counterparty_id,
            Counterparty.role == role,
        )
        .exists()
    )

    return bool(await connection.fetch_val(query))


async def fetch_batch_mv(connection: Connection, batch_id: int) -> Record | None:
    query = (
        Select(Batch.id, Batch.material_id, Batch.warehouse_id, Batch.remaining)
        .where(Batch.id == batch_id)
    )

    return await connection.fetch_row(query)


class InsufficientBatchesForFifoError(Exception):
    """Нет партии материала на складе под распределение факта (в т.ч. излишек)."""


async def allocate_inventory_adjustment_details_fifo(
    connection: Connection,
    warehouse_id: int,
    material_id: int,
    actual_qty: Decimal,
) -> list[tuple[int, Decimal]]:
    """Раскладывает факт строки инвентаризации по партиям: FIFO по остаткам, затем излишек на новейшую партию."""
    if actual_qty <= 0:
        return []

    stmt_fifo = (
        Select(Batch.id, Batch.remaining)
        .where(
            Batch.warehouse_id == warehouse_id,
            Batch.material_id == material_id,
        )
        .order_by(Batch.created_at.asc(), Batch.id.asc())
    )
    rows = await connection.fetch(stmt_fifo)

    details: list[tuple[int, Decimal]] = []
    leftover = actual_qty

    for row in rows:
        if leftover <= 0:
            break
        rem = row["remaining"]
        take = min(rem, leftover)
        if take > 0:
            details.append((int(row["id"]), take))
            leftover -= take

    if leftover > 0:
        stmt_new = (
            Select(Batch.id)
            .where(
                Batch.warehouse_id == warehouse_id,
                Batch.material_id == material_id,
            )
            .order_by(Batch.created_at.desc(), Batch.id.desc())
            .limit(1)
        )
        nrow = await connection.fetch_row(stmt_new)
        if nrow is None:
            raise InsufficientBatchesForFifoError

        nid = int(nrow["id"])
        for i, (bid, qty) in enumerate(details):
            if bid == nid:
                details[i] = (bid, qty + leftover)
                break
        else:
            details.append((nid, leftover))

    return details


async def find_fifo_batch_covering_quantity(
    connection: Connection,
    warehouse_id: int,
    material_id: int,
    quantity: Decimal,
) -> Record | None:
    """Партия с remaining >= quantity: самая ранняя по created_at, затем по id (FIFO)."""
    query = (
        Select(Batch.id, Batch.material_id, Batch.warehouse_id, Batch.remaining)
        .where(
            Batch.warehouse_id == warehouse_id,
            Batch.material_id == material_id,
            Batch.remaining >= quantity,
        )
        .order_by(Batch.created_at.asc(), Batch.id.asc())
        .limit(1)
    )

    return await connection.fetch_row(query)
