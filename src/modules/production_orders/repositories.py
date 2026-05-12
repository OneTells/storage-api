from typing import Any

from asyncpg import Record
from everbase import Connection
from orjson import loads
from sqlalchemy import Select, func, literal_column
from sqlalchemy.dialects.postgresql import aggregate_order_by
from sqlalchemy.orm import aliased

from core.models import (
    Employee,
    Material,
    Product,
    ProductionOrder,
    ProductionOrderMaterial,
    ProductionOrderProduct,
    ProductionOrderResource,
    ProductionOrderStatus,
    ProductionOrderWorker,
    ProductionOrderWriteOffWarehouse,
    Resource,
    User,
    Warehouse,
)

from modules.production_orders.schemes import (
    MaterialReservationRead,
    NamedEntityRef,
    ProductionOrderProductLineRead,
    ProductionOrderRead,
    ProductionOrderResourceLineRead,
    ProductionOrderWorkerLineRead,
)


def _parse_jsonb_column(val: Any) -> Any:
    if val is None:
        return []
    if isinstance(val, (list, dict)):
        return val
    if isinstance(val, (bytes, str)):
        return loads(val)
    return val


def _products_json_subquery():
    return (
        Select(
            func.coalesce(
                func.jsonb_agg(
                    aggregate_order_by(
                        func.jsonb_build_object(
                            "id",
                            ProductionOrderProduct.id,
                            "product",
                            func.jsonb_build_object("id", Product.id, "name", Product.name),
                            "quantity",
                            ProductionOrderProduct.quantity,
                        ),
                        ProductionOrderProduct.id.asc(),
                    )
                ),
                literal_column("'[]'::jsonb"),
            )
        )
        .select_from(ProductionOrderProduct)
        .join(Product, Product.id == ProductionOrderProduct.product_id)
        .where(ProductionOrderProduct.order_id == ProductionOrder.id)
        .scalar_subquery()
    )


def _resources_json_subquery():
    return (
        Select(
            func.coalesce(
                func.jsonb_agg(
                    aggregate_order_by(
                        func.jsonb_build_object(
                            "id",
                            ProductionOrderResource.id,
                            "resource",
                            func.jsonb_build_object("id", Resource.id, "name", Resource.name),
                            "quantity",
                            ProductionOrderResource.quantity,
                        ),
                        ProductionOrderResource.id.asc(),
                    )
                ),
                literal_column("'[]'::jsonb"),
            )
        )
        .select_from(ProductionOrderResource)
        .join(Resource, Resource.id == ProductionOrderResource.resource_id)
        .where(ProductionOrderResource.order_id == ProductionOrder.id)
        .scalar_subquery()
    )


def _workers_json_subquery():
    return (
        Select(
            func.coalesce(
                func.jsonb_agg(
                    aggregate_order_by(
                        func.jsonb_build_object(
                            "id",
                            ProductionOrderWorker.id,
                            "employee",
                            func.jsonb_build_object("id", Employee.id, "name", Employee.full_name),
                            "hours_worked",
                            ProductionOrderWorker.hours_worked,
                            "hourly_rate",
                            ProductionOrderWorker.hourly_rate,
                        ),
                        ProductionOrderWorker.id.asc(),
                    )
                ),
                literal_column("'[]'::jsonb"),
            )
        )
        .select_from(ProductionOrderWorker)
        .join(Employee, Employee.id == ProductionOrderWorker.employee_id)
        .where(ProductionOrderWorker.order_id == ProductionOrder.id)
        .scalar_subquery()
    )


def _materials_json_subquery():
    return (
        Select(
            func.coalesce(
                func.jsonb_agg(
                    aggregate_order_by(
                        func.jsonb_build_object(
                            "material",
                            func.jsonb_build_object(
                                "id",
                                Material.id,
                                "name",
                                Material.name,
                                "sku",
                                Material.sku,
                            ),
                            "reserved_quantity",
                            ProductionOrderMaterial.reservation_quantity,
                            "planned_quantity",
                            ProductionOrderMaterial.quantity,
                        ),
                        ProductionOrderMaterial.id.asc(),
                    )
                ),
                literal_column("'[]'::jsonb"),
            )
        )
        .select_from(ProductionOrderMaterial)
        .join(Material, Material.id == ProductionOrderMaterial.material_id)
        .where(ProductionOrderMaterial.order_id == ProductionOrder.id)
        .scalar_subquery()
    )


def _write_off_warehouses_json_subquery():
    return (
        Select(
            func.coalesce(
                func.jsonb_agg(
                    aggregate_order_by(
                        func.jsonb_build_object("id", Warehouse.id, "name", Warehouse.name),
                        Warehouse.id.asc(),
                    )
                ),
                literal_column("'[]'::jsonb"),
            )
        )
        .select_from(ProductionOrderWriteOffWarehouse)
        .join(Warehouse, Warehouse.id == ProductionOrderWriteOffWarehouse.warehouse_id)
        .where(ProductionOrderWriteOffWarehouse.order_id == ProductionOrder.id)
        .scalar_subquery()
    )


def _production_order_select_columns():
    dw = aliased(Warehouse)
    return (
        ProductionOrder.id,
        ProductionOrder.performed_at,
        ProductionOrder.comment,
        ProductionOrder.status,
        ProductionOrder.created_at,
        ProductionOrder.completed_at,
        ProductionOrder.closed_at,
        ProductionOrder.cancelled_at,
        ProductionOrder.warehouse_id,
        dw.name.label("delivery_warehouse_name"),
        User.id.label("created_by_id"),
        User.name.label("created_by_name"),
        _products_json_subquery().label("products"),
        _resources_json_subquery().label("resources"),
        _workers_json_subquery().label("workers"),
        _materials_json_subquery().label("materials"),
        _write_off_warehouses_json_subquery().label("write_off_warehouses"),
    ), dw


def production_order_read_from_row(row: Record) -> ProductionOrderRead:
    products_raw = _parse_jsonb_column(row["products"])
    resources_raw = _parse_jsonb_column(row["resources"])
    workers_raw = _parse_jsonb_column(row["workers"])
    materials_raw = _parse_jsonb_column(row["materials"])
    wh_raw = _parse_jsonb_column(row["write_off_warehouses"])

    products = [ProductionOrderProductLineRead.model_validate(p) for p in products_raw]
    resources = [ProductionOrderResourceLineRead.model_validate(r) for r in resources_raw]
    workers = [ProductionOrderWorkerLineRead.model_validate(w) for w in workers_raw]
    material_reservations = [MaterialReservationRead.model_validate(m) for m in materials_raw]
    write_off_warehouses = [NamedEntityRef.model_validate(w) for w in wh_raw]

    return ProductionOrderRead(
        id=row["id"],
        performed_at=row["performed_at"],
        delivery_warehouse=NamedEntityRef(id=row["warehouse_id"], name=row["delivery_warehouse_name"]),
        write_off_warehouses=write_off_warehouses,
        comment=row["comment"],
        status=row["status"],
        created_by=NamedEntityRef(id=row["created_by_id"], name=row["created_by_name"]),
        created_at=row["created_at"],
        completed_at=row["completed_at"],
        closed_at=row["closed_at"],
        cancelled_at=row["cancelled_at"],
        products=products,
        resources=resources,
        workers=workers,
        material_reservations=material_reservations,
    )


async def count_production_orders(
    connection: Connection,
    status: ProductionOrderStatus | None,
) -> int:
    stmt = Select(func.count()).select_from(ProductionOrder)
    if status is not None:
        stmt = stmt.where(ProductionOrder.status == status)
    val = await connection.fetch_val(stmt)
    return int(val or 0)


async def fetch_production_orders(
    connection: Connection,
    page: int,
    limit: int,
    status: ProductionOrderStatus | None,
) -> list[Record]:
    cols, dw = _production_order_select_columns()
    stmt = (
        Select(*cols)
        .select_from(ProductionOrder)
        .join(dw, dw.id == ProductionOrder.warehouse_id)
        .join(User, User.id == ProductionOrder.created_by_id)
        .order_by(ProductionOrder.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    if status is not None:
        stmt = stmt.where(ProductionOrder.status == status)
    return await connection.fetch(stmt)


async def get_production_order_row(connection: Connection, order_id: int) -> Record | None:
    cols, dw = _production_order_select_columns()
    stmt = (
        Select(*cols)
        .select_from(ProductionOrder)
        .join(dw, dw.id == ProductionOrder.warehouse_id)
        .join(User, User.id == ProductionOrder.created_by_id)
        .where(ProductionOrder.id == order_id)
    )
    return await connection.fetch_row(stmt)
