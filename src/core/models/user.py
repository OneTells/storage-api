import uuid
from datetime import datetime

from everbase import Base
from sqlalchemy import Enum, UUID, true, Boolean, ForeignKey, BigInteger, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import MappedColumn, mapped_column

from core.schemes.user import UserRole


class User(Base):
    __tablename__ = "users"

    id: MappedColumn[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    role: MappedColumn[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    # Тут ещё есть поля, заполнить потом

    is_active: MappedColumn[bool] = mapped_column(Boolean, nullable=False, server_default=true())

    created_at: MappedColumn[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


class UserSession(Base):
    __tablename__ = "user_sessions"

    id: MappedColumn[uuid.UUID] = mapped_column(UUID, primary_key=True)
    secret: MappedColumn[uuid.UUID] = mapped_column(UUID, primary_key=True)

    user_id: MappedColumn[int] = mapped_column(BigInteger, ForeignKey(User.id), nullable=False)

    is_active: MappedColumn[bool] = mapped_column(Boolean, nullable=False, server_default=true())

    created_at: MappedColumn[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    deactivated_at: MappedColumn[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
