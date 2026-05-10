from datetime import datetime

from sqlalchemy import BigInteger, Boolean, ForeignKey, func, Identity, TEXT, TIMESTAMP, true
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .units import Unit


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    sku: Mapped[str] = mapped_column(TEXT, unique=True)
    name: Mapped[str] = mapped_column(TEXT)
    description: Mapped[str] = mapped_column(TEXT)
    unit_id: Mapped[int] = mapped_column(ForeignKey(Unit.id))
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=true())
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())


class MaterialCategory(Base):
    __tablename__ = "material_categories"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(TEXT, unique=True)
    description: Mapped[str] = mapped_column(TEXT)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())


class MaterialCategoryMaterial(Base):
    __tablename__ = "material_category_materials"

    category_id: Mapped[int] = mapped_column(ForeignKey(MaterialCategory.id), primary_key=True)
    material_id: Mapped[int] = mapped_column(ForeignKey(Material.id), primary_key=True)


class MaterialCategorySubcategory(Base):
    __tablename__ = "material_category_subcategories"

    category_id: Mapped[int] = mapped_column(ForeignKey(MaterialCategory.id), primary_key=True)
    subcategory_id: Mapped[int] = mapped_column(ForeignKey(MaterialCategory.id, ondelete="CASCADE"), primary_key=True)
