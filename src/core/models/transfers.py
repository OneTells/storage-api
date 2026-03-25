import uuid
from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, func, Identity, Text, TIMESTAMP, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .object_units import ObjectUnit
from .users import User
from .warehouses import Warehouse


class Transfer(Base):
    __tablename__ = "transfers"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)

    source_warehouse_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Warehouse.id))
    destination_warehouse_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Warehouse.id))
    creator_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(User.id))

    name: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())


class TransferItem(Base):
    __tablename__ = "transfer_items"

    transfer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Transfer.id), primary_key=True)
    object_unit_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey(ObjectUnit.id), primary_key=True)
