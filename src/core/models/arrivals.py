import uuid
from datetime import datetime
from enum import auto, StrEnum

from sqlalchemy import BigInteger, Enum, ForeignKey, func, Text, TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .object_units import ObjectUnit
from .objects import Object
from .suppliers import Supplier
from .user import User
from .warehouses import Warehouse


class ArrivalStatus(StrEnum):
    DRAFT = auto()
    COMPLETED = auto()


class Arrival(Base):
    __tablename__ = "arrivals"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    supplier_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Supplier.id), nullable=False)

    name: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ArrivalStatus] = mapped_column(Enum(ArrivalStatus), nullable=False)

    creator_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(User.id), nullable=False)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


class ArrivalItem(Base):
    __tablename__ = "arrival_items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    arrival_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Arrival.id, ondelete="CASCADE"), nullable=False)
    object_unit_id: Mapped[uuid.UUID | None] = mapped_column(UUID, ForeignKey(ObjectUnit.id), nullable=True)

    object_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Object.id), nullable=False)
    warehouse_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Warehouse.id), nullable=False)
    price: Mapped[float] = mapped_column(BigInteger, nullable=False)
