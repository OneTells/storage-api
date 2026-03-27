import uuid
from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, func, Identity, Text, TIMESTAMP, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .object_units import ObjectUnit
from .users import User
from .warehouses import Warehouse


class WriteOff(Base):
    __tablename__ = "write_offs"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)

    warehouse_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Warehouse.id))
    creator_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(User.id))

    name: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())


class WriteOffItem(Base):
    __tablename__ = "write_off_items"

    write_off_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(WriteOff.id), primary_key=True)
    object_unit_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey(ObjectUnit.id), primary_key=True)

    reason: Mapped[str] = mapped_column(Text)
