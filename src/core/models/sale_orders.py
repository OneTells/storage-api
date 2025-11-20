from datetime import datetime
from enum import auto, StrEnum

from everbase import Base
from sqlalchemy import BigInteger, Text, ForeignKey, TIMESTAMP, func, Enum, PrimaryKeyConstraint
from sqlalchemy.orm import MappedColumn, mapped_column

from .user import User
from .object_units import ObjectUnit
from .suppliers import Supplier
from .warehouses import Warehouse


class SaleOrderStatus(StrEnum):
    DRAFT = auto()
    COMPLETED = auto()


class SaleOrder(Base):
    __tablename__ = "sale_orders"

    id: MappedColumn[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    supplier_id: MappedColumn[int] = mapped_column(BigInteger, ForeignKey(Supplier.id), nullable=False)

    name: MappedColumn[str] = mapped_column(Text, nullable=False)
    status: MappedColumn[SaleOrderStatus] = mapped_column(Enum(SaleOrderStatus), nullable=False)

    creator_id: MappedColumn[int] = mapped_column(BigInteger, ForeignKey(User.id), nullable=False)

    created_at: MappedColumn[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


class SaleOrderItem(Base):
    __tablename__ = "sale_order_items"

    sale_order_id: MappedColumn[int] = mapped_column(BigInteger, ForeignKey(SaleOrder.id), nullable=False)
    object_unit_id: MappedColumn[int] = mapped_column(BigInteger, ForeignKey(ObjectUnit.id), nullable=False)

    warehouse_id: MappedColumn[int] = mapped_column(BigInteger, ForeignKey(Warehouse.id), nullable=False)
    sale_price: MappedColumn[float] = mapped_column(BigInteger, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint(sale_order_id, object_unit_id),
    )
