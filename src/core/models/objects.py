from datetime import datetime

from everbase import Base
from sqlalchemy import BigInteger, TEXT, func, Boolean, true, ForeignKey, false
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import MappedColumn, mapped_column


class Object(Base):
    __tablename__ = "objects"

    id: MappedColumn[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    name: MappedColumn[str] = mapped_column(TEXT, nullable=False)
    is_active: MappedColumn[bool] = mapped_column(Boolean, nullable=False, server_default=true())

    created_at: MappedColumn[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


class Category(Base):
    __tablename__ = "categories"

    id: MappedColumn[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    name: MappedColumn[str] = mapped_column(TEXT, nullable=False)
    is_subcategory: MappedColumn[bool] = mapped_column(Boolean, nullable=False, server_default=false())

    created_at: MappedColumn[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


class ObjectCategory(Base):
    __tablename__ = "object_categories"

    object_id: MappedColumn[int] = mapped_column(BigInteger, ForeignKey(Object.id), primary_key=True, nullable=False)
    category_id: MappedColumn[int] = mapped_column(BigInteger, ForeignKey(Category.id), primary_key=True, nullable=False)


class CategorySubcategory(Base):
    __tablename__ = "category_subcategories"

    category_id: MappedColumn[int] = mapped_column(BigInteger, ForeignKey(Category.id), primary_key=True, nullable=False)
    subcategory_id: MappedColumn[int] = mapped_column(BigInteger, ForeignKey(Category.id), primary_key=True, nullable=False)
