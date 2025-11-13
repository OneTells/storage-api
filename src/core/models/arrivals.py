from datetime import datetime
from enum import auto, StrEnum

from everbase import Base
from sqlalchemy import BigInteger, Text, ForeignKey, TIMESTAMP, func, Enum
from sqlalchemy.orm import MappedColumn, mapped_column

from .user import User
from .objects import Object
from .object_units import ObjectUnit
from .suppliers import Supplier
from .warehouses import Warehouse


class ArrivalStatus(StrEnum):
    DRAFT = auto()
    COMPLETED = auto()


class Arrival(Base):
    __tablename__ = "arrivals"

    id: MappedColumn[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    supplier_id: MappedColumn[int] = mapped_column(BigInteger, ForeignKey(Supplier.id), nullable=False)

    name: MappedColumn[str] = mapped_column(Text, nullable=False)
    status: MappedColumn[ArrivalStatus] = mapped_column(Enum(ArrivalStatus), nullable=False)

    creator_id: MappedColumn[int] = mapped_column(BigInteger, ForeignKey(User.id), nullable=False)

    created_at: MappedColumn[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


class ArrivalItem(Base):
    __tablename__ = "arrival_items"

    id: MappedColumn[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    arrival_id: MappedColumn[int] = mapped_column(BigInteger, ForeignKey(Arrival.id, ondelete="CASCADE"), nullable=False)
    object_unit_id: MappedColumn[int | None] = mapped_column(BigInteger, ForeignKey(ObjectUnit.id), nullable=True)

    object_id: MappedColumn[int] = mapped_column(BigInteger, ForeignKey(Object.id), nullable=False)
    warehouse_id: MappedColumn[int] = mapped_column(BigInteger, ForeignKey(Warehouse.id), nullable=False)
    price: MappedColumn[float] = mapped_column(BigInteger, nullable=False)
