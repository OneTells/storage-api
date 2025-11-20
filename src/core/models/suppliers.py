from datetime import datetime

from everbase import Base
from sqlalchemy import TIMESTAMP, func, BigInteger, TEXT, Boolean, true
from sqlalchemy.orm import mapped_column, MappedColumn


class Supplier(Base):
    __tablename__ = "suppliers"

    id: MappedColumn[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    name: MappedColumn[str] = mapped_column(TEXT, nullable=False)
    is_active: MappedColumn[bool] = mapped_column(Boolean, nullable=False, server_default=true())

    created_at: MappedColumn[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
