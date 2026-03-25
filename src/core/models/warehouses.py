from datetime import datetime

from sqlalchemy import BigInteger, Boolean, func, Identity, TEXT, TIMESTAMP, true
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)

    name: Mapped[str] = mapped_column(TEXT, unique=True)
    address: Mapped[str] = mapped_column(TEXT)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=true())
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
