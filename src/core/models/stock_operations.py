from datetime import datetime
from enum import auto, StrEnum

from sqlalchemy import BigInteger, Enum, ForeignKey, func, Identity, Numeric, Text, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .customers import Customer
from .object_units import ObjectUnit, ObjectUnitStatus
from .suppliers import Supplier
from .users import User
from .warehouses import Warehouse


class StockOperationType(StrEnum):
    RECEIPT = auto()  # Приёмка от поставщика
    RETURN_FROM_PRODUCTION = auto()  # Возврат материалов из производства
    PRODUCTION_OUTPUT = auto()  # Выпуск готовой продукции
    RETURN_FROM_CUSTOMER = auto()  # Возврат от клиента

    WRITE_OFF_TO_PRODUCTION = auto()  # Списание в производство
    SHIPMENT = auto()  # Отгрузка клиенту
    RETURN_TO_SUPPLIER = auto()  # Возврат поставщику

    INVENTORY_ADJUSTMENT = auto()  # Инвентаризация / корректировка остатков
    TRANSFER_BETWEEN_WAREHOUSES = auto()  # Перемещение между складами
    RESERVATION = auto()  # Резервирование


class StockOperation(Base):
    __tablename__ = "stock_operations"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    type: Mapped[StockOperationType] = mapped_column(Enum(StockOperationType))
    name: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(User.id))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())


class StockOperationUnit(Base):
    __tablename__ = "stock_operation_units"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    operation_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(StockOperation.id, ondelete="CASCADE"), index=True)
    object_unit_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(ObjectUnit.id), index=True)

    old_warehouse_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey(Warehouse.id))
    new_warehouse_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey(Warehouse.id))

    old_status: Mapped[ObjectUnitStatus | None] = mapped_column(Enum(ObjectUnitStatus))
    new_status: Mapped[ObjectUnitStatus | None] = mapped_column(Enum(ObjectUnitStatus))


class ReceiptDetail(Base):
    __tablename__ = "receipt_details"

    operation_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(StockOperation.id, ondelete="CASCADE"), primary_key=True)
    supplier_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Supplier.id))


class ReceiptUnitDetail(Base):
    __tablename__ = "receipt_unit_details"

    unit_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(StockOperationUnit.id, ondelete="CASCADE"), primary_key=True)
    price: Mapped[float | None] = mapped_column(Numeric(12, 2))


class WriteOffToProductionDetail(Base):
    __tablename__ = "write_off_to_production_details"

    operation_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(StockOperation.id, ondelete="CASCADE"), primary_key=True)
    production_order_id: Mapped[int] = mapped_column(BigInteger)


class WriteOffToProductionUnitDetail(Base):
    __tablename__ = "write_off_to_production_unit_details"

    unit_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(StockOperationUnit.id, ondelete="CASCADE"), primary_key=True)


class ProductionOutputDetail(Base):
    __tablename__ = "production_output_details"

    operation_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(StockOperation.id, ondelete="CASCADE"), primary_key=True)
    production_order_id: Mapped[int] = mapped_column(BigInteger)


class ProductionOutputUnitDetail(Base):
    __tablename__ = "production_output_unit_details"

    unit_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(StockOperationUnit.id, ondelete="CASCADE"), primary_key=True)
    cost_price: Mapped[float | None] = mapped_column(Numeric(12, 2))


class ShipmentDetail(Base):
    __tablename__ = "shipment_details"

    operation_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(StockOperation.id, ondelete="CASCADE"), primary_key=True)
    customer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Customer.id))


class ShipmentUnitDetail(Base):
    __tablename__ = "shipment_unit_details"

    unit_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(StockOperationUnit.id, ondelete="CASCADE"), primary_key=True)
    sale_price: Mapped[float] = mapped_column(Numeric(12, 2))


class ReturnFromProductionDetail(Base):
    __tablename__ = "return_from_production_details"

    operation_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(StockOperation.id, ondelete="CASCADE"), primary_key=True)
    production_order_id: Mapped[int] = mapped_column(BigInteger)
    reason: Mapped[str | None] = mapped_column(Text)


class ReturnFromProductionUnitDetail(Base):
    __tablename__ = "return_from_production_unit_details"

    unit_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(StockOperationUnit.id, ondelete="CASCADE"), primary_key=True)
    reason: Mapped[str | None] = mapped_column(Text)


class InventoryAdjustmentDetail(Base):
    __tablename__ = "inventory_adjustment_details"

    operation_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(StockOperation.id, ondelete="CASCADE"), primary_key=True)
    inventory_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    reason: Mapped[str | None] = mapped_column(Text)


class InventoryAdjustmentUnitDetail(Base):
    __tablename__ = "inventory_adjustment_unit_details"

    unit_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(StockOperationUnit.id, ondelete="CASCADE"), primary_key=True)
    reason: Mapped[str | None] = mapped_column(Text)


class ReservationDetail(Base):
    __tablename__ = "reservation_details"

    operation_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(StockOperation.id, ondelete="CASCADE"), primary_key=True)
    order_id: Mapped[int] = mapped_column(BigInteger)


class ReservationUnitDetail(Base):
    __tablename__ = "reservation_unit_details"

    unit_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(StockOperationUnit.id, ondelete="CASCADE"), primary_key=True)


class ReturnToSupplierDetail(Base):
    __tablename__ = "return_to_supplier_details"

    operation_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(StockOperation.id, ondelete="CASCADE"), primary_key=True)
    supplier_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Supplier.id))
    reason: Mapped[str | None] = mapped_column(Text)


class ReturnToSupplierUnitDetail(Base):
    __tablename__ = "return_to_supplier_unit_details"

    unit_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(StockOperationUnit.id, ondelete="CASCADE"), primary_key=True)
    reason: Mapped[str | None] = mapped_column(Text)


class ReturnFromCustomerDetail(Base):
    __tablename__ = "return_from_customer_details"

    operation_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(StockOperation.id, ondelete="CASCADE"), primary_key=True)
    customer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Customer.id))
    reason: Mapped[str | None] = mapped_column(Text)


class ReturnFromCustomerUnitDetail(Base):
    __tablename__ = "return_from_customer_unit_details"

    unit_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(StockOperationUnit.id, ondelete="CASCADE"), primary_key=True)
    reason: Mapped[str | None] = mapped_column(Text)
    condition: Mapped[str | None] = mapped_column(Text)


class TransferDetail(Base):
    __tablename__ = "transfer_details"

    operation_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(StockOperation.id, ondelete="CASCADE"), primary_key=True)
    comment: Mapped[str | None] = mapped_column(Text)


class TransferUnitDetail(Base):
    __tablename__ = "transfer_unit_details"

    unit_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(StockOperationUnit.id, ondelete="CASCADE"), primary_key=True)
