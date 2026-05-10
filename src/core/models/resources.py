from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import BigInteger, Enum, ForeignKey, func, Identity, Numeric, TEXT, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .units import Unit


class ResourceType(StrEnum):
    FIXED_RATE = "FIXED_RATE"
    DEPRECIATION = "DEPRECIATION"


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    type: Mapped[ResourceType] = mapped_column(Enum(ResourceType))

    name: Mapped[str] = mapped_column(TEXT)
    unit_id: Mapped[int] = mapped_column(ForeignKey(Unit.id))

    # Для фиксированной ставки
    fixed_rate: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))

    # Для амортизации
    initial_amount: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    service_life: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
