from datetime import UTC, datetime
from typing import Any

from asyncpg import Record
from everbase import Connection
from sqlalchemy import Delete, literal_column, Select, Update, func
from sqlalchemy.dialects.postgresql import Insert, aggregate_order_by

from core.models import (
    OperationStatus,
    ProductionOrder,
    ProductionOutput,
    ProductionOutputItem,
    StockOperation,
    StockOperationType,
    User,
)

from modules.operations.production_output.schemes import ProductionOutputCreate, ProductionOutputUpdate


async def count_production_outputs(
    connection: Connection,
    user_id: int | None,
    created_from: datetime | None,
    created_to: datetime | None,
    status: OperationStatus | None,
) -> int:
    stmt = (
        Select(func.count())
        .select_from(ProductionOutput)
        .join(StockOperation, StockOperation.id == ProductionOutput.operation_id)
        .where(StockOperation.type == StockOperationType.PRODUCTION_OUTPUT)
    )

    if user_id is not None:
        stmt = stmt.where(StockOperation.created_by_id == user_id)

    if created_from is not None:
        stmt = stmt.where(StockOperation.created_at >= created_from)

    if created_to is not None:
        stmt = stmt.where(StockOperation.created_at <= created_to)

    if status is not None:
        stmt = stmt.where(ProductionOutput.status == status)

    return await connection.fetch_val(stmt, model=lambda x: int(x))


async def fetch_production_outputs(
    connection: Connection,
    page: int,
    limit: int,
    user_id: int | None,
    created_from: datetime | None,
    created_to: datetime | None,
    status: OperationStatus | None,
) -> list[Record]:
    poi = (
        Select(
            ProductionOutputItem.operation_id,
            func.json_agg(
                aggregate_order_by(
                    func.json_build_object(
                        "material_id",
                        ProductionOutputItem.material_id,
                        "quantity",
                        ProductionOutputItem.quantity,
                        "unit_price",
                        ProductionOutputItem.unit_price,
                        "batch_id",
                        ProductionOutputItem.batch_id,
                    ),
                    ProductionOutputItem.id.asc(),
                ),
            ).label("items_json"),
        )
        .group_by(ProductionOutputItem.operation_id)
    ).subquery("production_output_items_agg")
    stmt = (
        Select(
            StockOperation.id,
            StockOperation.name,
            StockOperation.performed_at,
            ProductionOutput.status,
            ProductionOutput.production_order_id,
            ProductionOrder.comment.label("production_order_comment"),
            ProductionOutput.warehouse_id,
            StockOperation.created_by_id,
            User.name.label("created_by_user_name"),
            StockOperation.created_at,
            StockOperation.completed_at,
            StockOperation.cancelled_at,
            func.coalesce(poi.c.items_json, literal_column("'[]'::json")).label("items"),
        )
        .select_from(ProductionOutput)
        .join(StockOperation, StockOperation.id == ProductionOutput.operation_id)
        .join(User, User.id == StockOperation.created_by_id)
        .join(ProductionOrder, ProductionOrder.id == ProductionOutput.production_order_id)
        .outerjoin(poi, poi.c.operation_id == StockOperation.id)
        .where(StockOperation.type == StockOperationType.PRODUCTION_OUTPUT)
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
        stmt = stmt.where(ProductionOutput.status == status)

    return await connection.fetch(stmt)


async def get_production_output(connection: Connection, operation_id: int) -> Record | None:
    poi = (
        Select(
            ProductionOutputItem.operation_id,
            func.json_agg(
                aggregate_order_by(
                    func.json_build_object(
                        "material_id",
                        ProductionOutputItem.material_id,
                        "quantity",
                        ProductionOutputItem.quantity,
                        "unit_price",
                        ProductionOutputItem.unit_price,
                        "batch_id",
                        ProductionOutputItem.batch_id,
                    ),
                    ProductionOutputItem.id.asc(),
                ),
            ).label("items_json"),
        )
        .group_by(ProductionOutputItem.operation_id)
    ).subquery("production_output_items_agg")
    stmt = (
        Select(
            StockOperation.id,
            StockOperation.name,
            StockOperation.performed_at,
            ProductionOutput.status,
            ProductionOutput.production_order_id,
            ProductionOrder.comment.label("production_order_comment"),
            ProductionOutput.warehouse_id,
            StockOperation.created_by_id,
            User.name.label("created_by_user_name"),
            StockOperation.created_at,
            StockOperation.completed_at,
            StockOperation.cancelled_at,
            func.coalesce(poi.c.items_json, literal_column("'[]'::json")).label("items"),
        )
        .select_from(ProductionOutput)
        .join(StockOperation, StockOperation.id == ProductionOutput.operation_id)
        .join(User, User.id == StockOperation.created_by_id)
        .join(ProductionOrder, ProductionOrder.id == ProductionOutput.production_order_id)
        .outerjoin(poi, poi.c.operation_id == StockOperation.id)
        .where(StockOperation.type == StockOperationType.PRODUCTION_OUTPUT, StockOperation.id == operation_id)
        .order_by(StockOperation.id.desc())
    )

    return await connection.fetch_row(stmt)


async def create_production_output(connection: Connection, user_id: int, payload: ProductionOutputCreate) -> int:
    async with connection.transaction():
        op_id = await connection.fetch_val(
            Insert(StockOperation)
            .values(
                type=StockOperationType.PRODUCTION_OUTPUT,
                name=payload.name,
                performed_at=payload.performed_at,
                created_by_id=user_id,
            )
            .returning(StockOperation.id)
        )

        await connection.execute(
            Insert(ProductionOutput).values(
                operation_id=op_id,
                production_order_id=payload.production_order_id,
                warehouse_id=payload.warehouse_id,
                status=OperationStatus.DRAFT,
            )
        )

        for it in payload.items:
            await connection.execute(
                Insert(ProductionOutputItem).values(
                    operation_id=op_id,
                    material_id=it.material_id,
                    quantity=it.quantity,
                    unit_price=it.unit_price,
                    batch_id=None,
                )
            )

    return int(op_id)


async def update_production_output(connection: Connection, operation_id: int, payload: ProductionOutputUpdate) -> None:
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

        p_vals: dict[str, Any] = {}

        if payload.production_order_id is not None:
            p_vals["production_order_id"] = payload.production_order_id

        if payload.warehouse_id is not None:
            p_vals["warehouse_id"] = payload.warehouse_id

        if payload.status is not None:
            p_vals["status"] = payload.status

        if p_vals:
            await connection.execute(
                Update(ProductionOutput).where(ProductionOutput.operation_id == operation_id).values(**p_vals)
            )

        if payload.items is not None:
            await connection.execute(Delete(ProductionOutputItem).where(ProductionOutputItem.operation_id == operation_id))

            for it in payload.items:
                await connection.execute(
                    Insert(ProductionOutputItem).values(
                        operation_id=operation_id,
                        material_id=it.material_id,
                        quantity=it.quantity,
                        unit_price=it.unit_price,
                        batch_id=None,
                    )
                )
