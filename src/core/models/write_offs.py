import uuid
from datetime import datetime
from enum import auto, StrEnum

from everbase import Base
from sqlalchemy import BigInteger, Text, ForeignKey, TIMESTAMP, func, Enum, PrimaryKeyConstraint, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .user import User
from .object_units import ObjectUnit
from .suppliers import Supplier
from .warehouses import Warehouse


class WriteOffStatus(StrEnum):
    DRAFT = auto()
    COMPLETED = auto()


class WriteOff(Base):
    __tablename__ = "write_offs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    supplier_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Supplier.id), nullable=False)

    name: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[WriteOffStatus] = mapped_column(Enum(WriteOffStatus), nullable=False)

    creator_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(User.id), nullable=False)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


class WriteOffItem(Base):
    __tablename__ = "write_off_items"

    write_off_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(WriteOff.id), nullable=False)
    object_unit_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey(ObjectUnit.id), nullable=False)

    warehouse_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Warehouse.id), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint(write_off_id, object_unit_id),
    )
