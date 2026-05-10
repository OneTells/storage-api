from datetime import datetime
from decimal import Decimal
from enum import auto, StrEnum

from sqlalchemy import BigInteger, Enum, ForeignKey, func, Identity, Numeric, String, Text, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from core.models.counterparties import Counterparty
from core.models.materials import Material
from core.models.users import User
from core.models.warehouses import Warehouse
from . import ProductionOrder
from .base import Base
from .batches import Batch


class OperationStatus(StrEnum):
    DRAFT = "DRAFT"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


# ---- 1. Приёмка от поставщика ----
class ReceiptStatus(StrEnum):
    DRAFT = "DRAFT"
    ORDERED = "ORDERED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Receipt(Base):
    __tablename__ = "receipts"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)

    performed_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    counterparty_id: Mapped[int] = mapped_column(ForeignKey(Counterparty.id))
    warehouse_id: Mapped[int] = mapped_column(ForeignKey(Warehouse.id))

    shipping_price: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    discount: Mapped[Decimal] = mapped_column(Numeric(15, 2))

    status: Mapped[ReceiptStatus] = mapped_column(Enum(ReceiptStatus), server_default=ReceiptStatus.DRAFT)

    created_by_id: Mapped[int] = mapped_column(ForeignKey(User.id))

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))


class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    operation_id: Mapped[int] = mapped_column(ForeignKey(Receipt.id, ondelete="CASCADE"))

    material_id: Mapped[int] = mapped_column(ForeignKey(Material.id))
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(15, 2))

    batch_id: Mapped[int | None] = mapped_column(ForeignKey(Batch.id))


# ---- 2. Выпуск готовой продукции (из производства) ----
class ProductionOutput(Base):
    __tablename__ = "production_outputs"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)

    performed_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    production_order_id: Mapped[int] = mapped_column(ForeignKey(ProductionOrder.id))
    warehouse_id: Mapped[int] = mapped_column(ForeignKey(Warehouse.id))

    status: Mapped[OperationStatus] = mapped_column(Enum(OperationStatus), server_default=OperationStatus.DRAFT)

    created_by_id: Mapped[int] = mapped_column(ForeignKey(User.id))

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))


class ProductionOutputItem(Base):
    __tablename__ = "production_output_items"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    operation_id: Mapped[int] = mapped_column(ForeignKey(ProductionOutput.id, ondelete="CASCADE"))

    material_id: Mapped[int] = mapped_column(ForeignKey(Material.id))
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(15, 2))

    batch_id: Mapped[int | None] = mapped_column(ForeignKey(Batch.id))


# ---- 3. Списание в производство ----
class WriteOffToProduction(Base):
    __tablename__ = "write_offs_to_production"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)

    performed_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    warehouse_id: Mapped[int] = mapped_column(ForeignKey(Warehouse.id))
    production_order_id: Mapped[str | None] = mapped_column(String(100))

    status: Mapped[OperationStatus] = mapped_column(Enum(OperationStatus), server_default=OperationStatus.DRAFT)

    created_by_id: Mapped[int] = mapped_column(ForeignKey(User.id))

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))


class WriteOffToProductionItem(Base):
    __tablename__ = "write_off_to_production_items"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    operation_id: Mapped[int] = mapped_column(ForeignKey(WriteOffToProduction.id, ondelete="CASCADE"))

    material_id: Mapped[int] = mapped_column(ForeignKey(Material.id))
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(15, 2))

    batch_id: Mapped[int | None] = mapped_column(ForeignKey(Batch.id))


# ---- 4. Отгрузка клиенту ----
class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)

    performed_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    counterparty_id: Mapped[int] = mapped_column(ForeignKey(Counterparty.id))
    warehouse_id: Mapped[int] = mapped_column(ForeignKey(Warehouse.id))
    order_number: Mapped[str | None] = mapped_column(String(100))

    status: Mapped[OperationStatus] = mapped_column(Enum(OperationStatus), server_default=OperationStatus.DRAFT)

    created_by_id: Mapped[int] = mapped_column(ForeignKey(User.id))

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))


class ShipmentItem(Base):
    __tablename__ = "shipment_items"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    operation_id: Mapped[int] = mapped_column(ForeignKey(Shipment.id, ondelete="CASCADE"))

    material_id: Mapped[int] = mapped_column(ForeignKey(Material.id))
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3))

    batch_id: Mapped[int | None] = mapped_column(ForeignKey(Batch.id))


# ---- 5. Инвентаризация / корректировка остатков ----
class InventoryAdjustment(Base):
    __tablename__ = "inventory_adjustments"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)

    performed_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    warehouse_id: Mapped[int] = mapped_column(ForeignKey(Warehouse.id))
    description: Mapped[str] = mapped_column(Text)

    status: Mapped[OperationStatus] = mapped_column(Enum(OperationStatus), server_default=OperationStatus.DRAFT)

    created_by_id: Mapped[int] = mapped_column(ForeignKey(User.id))

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))


class InventoryAdjustmentItem(Base):
    __tablename__ = "inventory_adjustment_items"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    operation_id: Mapped[int] = mapped_column(ForeignKey(InventoryAdjustment.id, ondelete="CASCADE"))

    material_id: Mapped[int] = mapped_column(ForeignKey(Material.id))

    expected_qty: Mapped[Decimal] = mapped_column(Numeric(15, 3))  # учётное количество
    actual_qty: Mapped[Decimal] = mapped_column(Numeric(15, 3))  # фактическое


class InventoryAdjustmentItemDetails(Base):
    __tablename__ = "inventory_adjustment_item_details"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey(InventoryAdjustmentItem.id, ondelete="CASCADE"))

    batch_id: Mapped[int] = mapped_column(ForeignKey(Batch.id))
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3))


# ---- 6. Перемещение между складами ----
class Transfer(Base):
    __tablename__ = "transfers"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)

    performed_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    from_warehouse_id: Mapped[int] = mapped_column(ForeignKey(Warehouse.id))
    to_warehouse_id: Mapped[int] = mapped_column(ForeignKey(Warehouse.id))

    status: Mapped[OperationStatus] = mapped_column(Enum(OperationStatus), server_default=OperationStatus.DRAFT)

    created_by_id: Mapped[int] = mapped_column(ForeignKey(User.id))

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))


class TransferItem(Base):
    __tablename__ = "transfer_items"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    operation_id: Mapped[int] = mapped_column(ForeignKey(Transfer.id, ondelete="CASCADE"))

    material_id: Mapped[int] = mapped_column(ForeignKey(Material.id))
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3))

    old_batch_id: Mapped[int | None] = mapped_column(ForeignKey(Batch.id))
    new_batch_id: Mapped[int | None] = mapped_column(ForeignKey(Batch.id))


# ---- 7. Резервирование ----
class ReservationStatus(StrEnum):
    ACTIVE = "ACTIVE"
    RELEASED = "RELEASED"
    CANCELLED = "CANCELLED"


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)

    batch_id: Mapped[int] = mapped_column(ForeignKey(Batch.id))
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3))

    status: Mapped[ReservationStatus] = mapped_column(Enum(ReservationStatus), server_default=ReservationStatus.ACTIVE)

    created_by_id: Mapped[int] = mapped_column(ForeignKey(User.id))

    reserved_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    released_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))


# ---- 8. Прочее списание (порча, утеря, и т.п.) ----
class WriteOff(Base):
    __tablename__ = "write_offs"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)

    performed_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    warehouse_id: Mapped[int] = mapped_column(ForeignKey(Warehouse.id))
    reason: Mapped[str] = mapped_column(Text)

    status: Mapped[OperationStatus] = mapped_column(Enum(OperationStatus), server_default=OperationStatus.DRAFT)

    created_by_id: Mapped[int] = mapped_column(ForeignKey(User.id))

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))


class WriteOffItem(Base):
    __tablename__ = "write_off_items_general"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    operation_id: Mapped[int] = mapped_column(ForeignKey(WriteOff.id, ondelete="CASCADE"))

    material_id: Mapped[int] = mapped_column(ForeignKey(Material.id))
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3))
    reason: Mapped[str] = mapped_column(Text)

    batch_id: Mapped[int | None] = mapped_column(ForeignKey(Batch.id))
