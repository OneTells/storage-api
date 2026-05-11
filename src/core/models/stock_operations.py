from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import BigInteger, Enum, ForeignKey, func, Identity, Numeric, String, Text, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .batches import Batch
from .counterparties import Counterparty
from .materials import Material
from .production_orders import ProductionOrder
from .users import User
from .warehouses import Warehouse


class StockOperationType(StrEnum):
    RECEIPT = "RECEIPT"
    SHIPMENT = "SHIPMENT"
    PRODUCTION_OUTPUT = "PRODUCTION_OUTPUT"
    WRITE_OFF_TO_PRODUCTION = "WRITE_OFF_TO_PRODUCTION"
    WRITE_OFF = "WRITE_OFF"
    INVENTORY_ADJUSTMENT = "INVENTORY_ADJUSTMENT"
    TRANSFER = "TRANSFER"
    RESERVATION = "RESERVATION"


class OperationStatus(StrEnum):
    DRAFT = "DRAFT"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class StockOperation(Base):
    __tablename__ = "stock_operations"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    type: Mapped[StockOperationType] = mapped_column(Enum(StockOperationType))

    name: Mapped[str] = mapped_column(String(255))

    performed_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))

    created_by_id: Mapped[int] = mapped_column(ForeignKey(User.id))

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))


# ---- 1. Приёмка от поставщика ----
class ReceiptStatus(StrEnum):
    DRAFT = "DRAFT"
    ORDERED = "ORDERED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Receipt(Base):
    __tablename__ = "receipts"

    operation_id: Mapped[int] = mapped_column(ForeignKey(StockOperation.id, ondelete="CASCADE"), primary_key=True)

    counterparty_id: Mapped[int] = mapped_column(ForeignKey(Counterparty.id))
    warehouse_id: Mapped[int] = mapped_column(ForeignKey(Warehouse.id))

    shipping_price: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    discount: Mapped[Decimal] = mapped_column(Numeric(15, 2))

    status: Mapped[ReceiptStatus] = mapped_column(Enum(ReceiptStatus), server_default=ReceiptStatus.DRAFT)


class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    operation_id: Mapped[int] = mapped_column(ForeignKey(StockOperation.id, ondelete="CASCADE"))

    material_id: Mapped[int] = mapped_column(ForeignKey(Material.id))
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(15, 2))

    batch_id: Mapped[int | None] = mapped_column(ForeignKey(Batch.id))


# ---- 2. Выпуск готовой продукции (из производства) ----
class ProductionOutput(Base):
    __tablename__ = "production_outputs"

    operation_id: Mapped[int] = mapped_column(ForeignKey(StockOperation.id, ondelete="CASCADE"), primary_key=True)

    production_order_id: Mapped[int] = mapped_column(ForeignKey(ProductionOrder.id))
    warehouse_id: Mapped[int] = mapped_column(ForeignKey(Warehouse.id))

    status: Mapped[OperationStatus] = mapped_column(Enum(OperationStatus), server_default=OperationStatus.DRAFT)


class ProductionOutputItem(Base):
    __tablename__ = "production_output_items"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    operation_id: Mapped[int] = mapped_column(ForeignKey(StockOperation.id, ondelete="CASCADE"))

    material_id: Mapped[int] = mapped_column(ForeignKey(Material.id))
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(15, 2))

    batch_id: Mapped[int | None] = mapped_column(ForeignKey(Batch.id))


# ---- 3. Списание в производство ----
class WriteOffToProduction(Base):
    __tablename__ = "write_offs_to_production"

    operation_id: Mapped[int] = mapped_column(ForeignKey(StockOperation.id, ondelete="CASCADE"), primary_key=True)

    warehouse_id: Mapped[int] = mapped_column(ForeignKey(Warehouse.id))
    production_order_id: Mapped[str | None] = mapped_column(String(100))

    status: Mapped[OperationStatus] = mapped_column(Enum(OperationStatus), server_default=OperationStatus.DRAFT)


class WriteOffToProductionItem(Base):
    __tablename__ = "write_off_to_production_items"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    operation_id: Mapped[int] = mapped_column(ForeignKey(StockOperation.id, ondelete="CASCADE"))

    material_id: Mapped[int] = mapped_column(ForeignKey(Material.id))
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(15, 2))

    batch_id: Mapped[int | None] = mapped_column(ForeignKey(Batch.id))


# ---- 4. Отгрузка клиенту ----
class Shipment(Base):
    __tablename__ = "shipments"

    operation_id: Mapped[int] = mapped_column(ForeignKey(StockOperation.id, ondelete="CASCADE"), primary_key=True)

    counterparty_id: Mapped[int] = mapped_column(ForeignKey(Counterparty.id))
    warehouse_id: Mapped[int] = mapped_column(ForeignKey(Warehouse.id))
    order_number: Mapped[str | None] = mapped_column(String(100))

    status: Mapped[OperationStatus] = mapped_column(Enum(OperationStatus), server_default=OperationStatus.DRAFT)


class ShipmentItem(Base):
    __tablename__ = "shipment_items"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    operation_id: Mapped[int] = mapped_column(ForeignKey(StockOperation.id, ondelete="CASCADE"))

    material_id: Mapped[int] = mapped_column(ForeignKey(Material.id))
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3))

    batch_id: Mapped[int | None] = mapped_column(ForeignKey(Batch.id))


# ---- 5. Инвентаризация / корректировка остатков ----
class InventoryAdjustment(Base):
    __tablename__ = "inventory_adjustments"

    operation_id: Mapped[int] = mapped_column(ForeignKey(StockOperation.id, ondelete="CASCADE"), primary_key=True)

    warehouse_id: Mapped[int] = mapped_column(ForeignKey(Warehouse.id))
    description: Mapped[str] = mapped_column(Text)

    status: Mapped[OperationStatus] = mapped_column(Enum(OperationStatus), server_default=OperationStatus.DRAFT)


class InventoryAdjustmentItem(Base):
    __tablename__ = "inventory_adjustment_items"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    operation_id: Mapped[int] = mapped_column(ForeignKey(StockOperation.id, ondelete="CASCADE"))

    material_id: Mapped[int] = mapped_column(ForeignKey(Material.id))

    expected_qty: Mapped[Decimal] = mapped_column(Numeric(15, 3))
    actual_qty: Mapped[Decimal] = mapped_column(Numeric(15, 3))


class InventoryAdjustmentItemDetails(Base):
    __tablename__ = "inventory_adjustment_item_details"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey(InventoryAdjustmentItem.id, ondelete="CASCADE"))

    batch_id: Mapped[int] = mapped_column(ForeignKey(Batch.id))
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3))


# ---- 6. Перемещение между складами ----
class Transfer(Base):
    __tablename__ = "transfers"

    operation_id: Mapped[int] = mapped_column(ForeignKey(StockOperation.id, ondelete="CASCADE"), primary_key=True)

    from_warehouse_id: Mapped[int] = mapped_column(ForeignKey(Warehouse.id))
    to_warehouse_id: Mapped[int] = mapped_column(ForeignKey(Warehouse.id))

    status: Mapped[OperationStatus] = mapped_column(Enum(OperationStatus), server_default=OperationStatus.DRAFT)


class TransferItem(Base):
    __tablename__ = "transfer_items"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    operation_id: Mapped[int] = mapped_column(ForeignKey(StockOperation.id, ondelete="CASCADE"))

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

    operation_id: Mapped[int] = mapped_column(ForeignKey(StockOperation.id, ondelete="CASCADE"), primary_key=True)

    batch_id: Mapped[int] = mapped_column(ForeignKey(Batch.id))
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3))

    status: Mapped[ReservationStatus] = mapped_column(Enum(ReservationStatus), server_default=ReservationStatus.ACTIVE)


# ---- 8. Прочее списание (порча, утеря, и т.п.) ----
class WriteOff(Base):
    __tablename__ = "write_offs"

    operation_id: Mapped[int] = mapped_column(ForeignKey(StockOperation.id, ondelete="CASCADE"), primary_key=True)

    warehouse_id: Mapped[int] = mapped_column(ForeignKey(Warehouse.id))
    reason: Mapped[str] = mapped_column(Text)

    status: Mapped[OperationStatus] = mapped_column(Enum(OperationStatus), server_default=OperationStatus.DRAFT)


class WriteOffItem(Base):
    __tablename__ = "write_off_items_general"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    operation_id: Mapped[int] = mapped_column(ForeignKey(StockOperation.id, ondelete="CASCADE"))

    material_id: Mapped[int] = mapped_column(ForeignKey(Material.id))
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3))
    reason: Mapped[str] = mapped_column(Text)

    batch_id: Mapped[int | None] = mapped_column(ForeignKey(Batch.id))
