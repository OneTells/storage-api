from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, func, Identity, Numeric, TEXT, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    full_name: Mapped[str] = mapped_column(TEXT, nullable=False)
    position: Mapped[str | None] = mapped_column(TEXT)
    default_hourly_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
