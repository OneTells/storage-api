from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, func, Identity, Numeric, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .objects import Object
from .warehouses import Warehouse


class Batch(Base):
    __tablename__ = "batches"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    object_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Object.id))
    warehouse_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Warehouse.id))
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3))  # начальное количество
    remaining: Mapped[Decimal] = mapped_column(Numeric(15, 3))  # текущий остаток
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("quantity >= 0", name="check_batch_quantity_non_negative"),
        CheckConstraint("remaining >= 0", name="check_batch_remaining_non_negative"),
    )
