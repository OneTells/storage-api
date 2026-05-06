from datetime import datetime
from decimal import Decimal
from enum import auto, StrEnum

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, Enum, false, ForeignKey, func,
    Identity, Index, Numeric, TEXT, text, TIMESTAMP, true
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class UnitCategoryEnum(StrEnum):
    QUANTITY = "QUANTITY"  # Количество
    WEIGHT = "WEIGHT"  # Вес
    VOLUME = "VOLUME"  # Объём
    LENGTH = "LENGTH"  # Длина
    AREA = "AREA"  # Площадь
    TIME = "TIME"  # Время
    ELECTRICITY = "ELECTRICITY"  # Электроэнергия


class Unit(Base):
    __tablename__ = "units"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    category: Mapped[UnitCategoryEnum] = mapped_column(Enum(UnitCategoryEnum))
    name: Mapped[str] = mapped_column(TEXT)
    short_name: Mapped[str] = mapped_column(TEXT)
    conversion_factor: Mapped[Decimal] = mapped_column(Numeric(20, 10), server_default=text('1.0'))
    is_base: Mapped[bool] = mapped_column(Boolean, server_default=false())
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("conversion_factor > 0", name="check_conv_factor_positive"),
        Index("ix_units_category", "category"),
        Index("ix_units_short_name", "short_name")
    )


class Object(Base):
    __tablename__ = "objects"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    sku: Mapped[str] = mapped_column(TEXT, unique=True)
    name: Mapped[str] = mapped_column(TEXT)
    description: Mapped[str] = mapped_column(TEXT)
    unit_id: Mapped[int] = mapped_column(ForeignKey(Unit.id))
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=true())
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
