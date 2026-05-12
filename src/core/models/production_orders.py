from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import BigInteger, Enum, ForeignKey, func, Identity, Numeric, TEXT, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .employees import Employee
from .materials import Material
from .products import Product
from .resources import Resource
from .users import User
from .warehouses import Warehouse


class ProductionOrderStatus(StrEnum):
    PLAN = "PLAN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class ProductionOrder(Base):
    __tablename__ = "production_orders"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)

    performed_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    warehouse_id: Mapped[int] = mapped_column(ForeignKey(Warehouse.id))
    comment: Mapped[str] = mapped_column(TEXT)

    status: Mapped[ProductionOrderStatus] = mapped_column(Enum(ProductionOrderStatus), default=ProductionOrderStatus.PLAN)

    created_by_id: Mapped[int] = mapped_column(ForeignKey(User.id))

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    closed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))


class ProductionOrderProduct(Base):
    __tablename__ = "production_order_products"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey(ProductionOrder.id, ondelete="CASCADE"))

    product_id: Mapped[int] = mapped_column(ForeignKey(Product.id))
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3))


class ProductionOrderResource(Base):
    __tablename__ = "production_order_resources"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey(ProductionOrder.id, ondelete="CASCADE"))

    resource_id: Mapped[int] = mapped_column(ForeignKey(Resource.id))
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3))


class ProductionOrderWorker(Base):
    __tablename__ = "production_order_workers"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey(ProductionOrder.id, ondelete="CASCADE"))

    employee_id: Mapped[int] = mapped_column(ForeignKey(Employee.id))
    hours_worked: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    hourly_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2))


class ProductionOrderMaterial(Base):
    __tablename__ = "production_order_materials"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    order_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(ProductionOrder.id, ondelete="CASCADE"))

    material_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Material.id))
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3))
    reservation_quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3))


class ProductionOrderReservation(Base):
    __tablename__ = "production_order_reservations"

    order_material_id: Mapped[int] = mapped_column(ForeignKey(ProductionOrderMaterial.id, ondelete="CASCADE"), primary_key=True)
    operation_id: Mapped[int] = mapped_column(ForeignKey("stock_operations.id", ondelete="CASCADE"), primary_key=True)


class ProductionOrderWriteOffWarehouse(Base):
    __tablename__ = "production_order_write_off_warehouses"

    order_id: Mapped[int] = mapped_column(ForeignKey(ProductionOrder.id, ondelete="CASCADE"), primary_key=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey(Warehouse.id), primary_key=True)
