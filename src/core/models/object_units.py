import uuid
from datetime import datetime
from enum import auto, StrEnum

from sqlalchemy import BigInteger, Enum, ForeignKey, Index, text, UUID
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .base import Base
from .objects import Object
from .warehouses import Warehouse


class ObjectUnitStatus(StrEnum):
    DEFAULT = auto()
    RESERVED = auto()
    SOLD = auto()
    WRITTEN_OFF = auto()


class ObjectUnit(Base):
    __tablename__ = "object_units"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, server_default=text("uuid_generate_v4()"))

    object_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Object.id), nullable=False)
    warehouse_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Warehouse.id), nullable=False)

    status: Mapped[ObjectUnitStatus] = mapped_column(Enum(ObjectUnitStatus), nullable=False)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        Index('idx_object_unit_warehouse', object_id, warehouse_id),
    )
