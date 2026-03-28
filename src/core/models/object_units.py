import uuid
from datetime import datetime
from enum import auto, StrEnum

from sqlalchemy import BigInteger, Enum, ForeignKey, Index, TIMESTAMP, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .base import Base
from .objects import Object
from .warehouses import Warehouse


class ObjectUnitStatus(StrEnum):
    DEFAULT = auto()
    RESERVED = auto()
    DEFECTIVE = auto()
    WRITTEN_OFF = auto()


class ObjectUnit(Base):
    __tablename__ = "object_units"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=func.uuidv7())

    object_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Object.id))
    warehouse_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Warehouse.id))

    status: Mapped[ObjectUnitStatus] = mapped_column(Enum(ObjectUnitStatus))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_object_unit_warehouse', object_id, warehouse_id),
    )
