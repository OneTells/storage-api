import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DOUBLE_PRECISION, ForeignKey, func, Identity, Text, TIMESTAMP, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .object_units import ObjectUnit
from .suppliers import Supplier
from .users import User
from .warehouses import Warehouse


class Arrival(Base):
    __tablename__ = "arrivals"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)

    supplier_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Supplier.id))
    warehouse_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Warehouse.id))
    creator_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(User.id))

    name: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())


class ArrivalItem(Base):
    __tablename__ = "arrival_items"

    arrival_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Arrival.id), primary_key=True)
    object_unit_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey(ObjectUnit.id), primary_key=True)

    price: Mapped[float] = mapped_column(DOUBLE_PRECISION)
