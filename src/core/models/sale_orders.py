import uuid
from datetime import datetime
from enum import auto, StrEnum

from sqlalchemy import BigInteger, Enum, ForeignKey, func, PrimaryKeyConstraint, Text, TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .object_units import ObjectUnit
from .suppliers import Supplier
from .user import User
from .warehouses import Warehouse


class SaleOrderStatus(StrEnum):
    DRAFT = auto()
    COMPLETED = auto()


class SaleOrder(Base):
    __tablename__ = "sale_orders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    supplier_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Supplier.id), nullable=False)

    name: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[SaleOrderStatus] = mapped_column(Enum(SaleOrderStatus), nullable=False)

    creator_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(User.id), nullable=False)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


class SaleOrderItem(Base):
    __tablename__ = "sale_order_items"

    sale_order_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(SaleOrder.id), nullable=False)
    object_unit_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey(ObjectUnit.id), nullable=False)

    warehouse_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Warehouse.id), nullable=False)
    sale_price: Mapped[float] = mapped_column(BigInteger, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint(sale_order_id, object_unit_id),
    )
