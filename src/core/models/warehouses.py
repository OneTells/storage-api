from datetime import datetime

from everbase import Base
from sqlalchemy import BigInteger, TEXT, func, Boolean, true
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import MappedColumn, mapped_column


class Warehouse(Base):
    __tablename__ = "warehouses"

    id: MappedColumn[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    name: MappedColumn[str] = mapped_column(TEXT, nullable=False)
    address: MappedColumn[str] = mapped_column(TEXT, nullable=False)
    is_active: MappedColumn[bool] = mapped_column(Boolean, nullable=False, server_default=true())

    created_at: MappedColumn[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
