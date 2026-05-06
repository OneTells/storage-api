from datetime import datetime
from enum import auto, StrEnum

from sqlalchemy import BigInteger, Boolean, Enum, func, Identity, TEXT, TIMESTAMP, true
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class CounterpartyRoleType(StrEnum):
    SUPPLIER = "SUPPLIER"  # Поставщик
    CUSTOMER = "CUSTOMER"  # Покупатель


class CounterpartyType(StrEnum):
    INDIVIDUAL = "INDIVIDUAL"  # Физическое лицо
    LEGAL_ENTITY = "LEGAL_ENTITY"  # Юридическое лицо
    ENTREPRENEUR = "ENTREPRENEUR"  # Индивидуальный предприниматель


class Counterparty(Base):
    __tablename__ = "counterparties"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    role: Mapped[CounterpartyRoleType] = mapped_column(Enum(CounterpartyRoleType))
    type: Mapped[CounterpartyType] = mapped_column(Enum(CounterpartyType))

    # Общие поля для всех типов
    name: Mapped[str] = mapped_column(TEXT)
    phone: Mapped[str | None] = mapped_column(TEXT)
    email: Mapped[str | None] = mapped_column(TEXT)
    comment: Mapped[str] = mapped_column(TEXT)

    # Поля только для юридического лица и ИП
    inn: Mapped[str | None] = mapped_column(TEXT)
    kpp: Mapped[str | None] = mapped_column(TEXT)  # только для юр.лица
    ogrn: Mapped[str | None] = mapped_column(TEXT)  # ОГРН/ОГРНИП
    legal_address: Mapped[str | None] = mapped_column(TEXT)

    # Поля только для юридического лица
    director: Mapped[str | None] = mapped_column(TEXT)  # Руководитель
    director_position: Mapped[str | None] = mapped_column(TEXT)  # Должность руководителя

    is_active: Mapped[bool] = mapped_column(Boolean, server_default=true())
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
