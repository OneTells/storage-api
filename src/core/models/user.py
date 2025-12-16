import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Enum, ForeignKey, func, true, UUID
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from core.schemas.user import UserRole
from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    # Тут ещё есть поля, заполнить потом

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=true())

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)
    secret: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(User.id), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=true())

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    deactivated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
