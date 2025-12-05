from datetime import datetime

from everbase import Base
from sqlalchemy import BigInteger, TEXT, func, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import mapped_column, Mapped

from .objects import Object


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(TEXT, nullable=False)
    description: Mapped[str] = mapped_column(TEXT, nullable=False)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


class CategoryObject(Base):
    __tablename__ = "category_objects"

    category_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Category.id), primary_key=True)
    object_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Object.id), primary_key=True)


class CategorySubcategory(Base):
    __tablename__ = "category_subcategories"

    category_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Category.id), primary_key=True)
    subcategory_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Category.id, ondelete="CASCADE"), primary_key=True)
