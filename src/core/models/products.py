from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, ForeignKey, func, Identity, Numeric, Text, TEXT, TIMESTAMP, true
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .materials import Material
from .resources import Resource


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)

    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)

    output_material_id: Mapped[int] = mapped_column(ForeignKey(Material.id))
    output_quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3), default=1)

    is_active: Mapped[bool] = mapped_column(Boolean, server_default=true())

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())


class ProductMaterial(Base):
    __tablename__ = "product_materials"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey(Product.id, ondelete="CASCADE"))

    material_id: Mapped[int] = mapped_column(ForeignKey(Material.id))
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3))


class ProductResource(Base):
    __tablename__ = "product_resources"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey(Product.id, ondelete="CASCADE"))

    resource_id: Mapped[int] = mapped_column(ForeignKey(Resource.id))
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3))


class ProductCategory(Base):
    __tablename__ = "product_categories"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(TEXT, unique=True)
    description: Mapped[str] = mapped_column(TEXT)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())


class ProductCategoryProduct(Base):
    __tablename__ = "product_category_products"

    category_id: Mapped[int] = mapped_column(ForeignKey(ProductCategory.id), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey(Product.id), primary_key=True)


class ProductCategorySubcategory(Base):
    __tablename__ = "product_category_subcategories"

    category_id: Mapped[int] = mapped_column(ForeignKey(ProductCategory.id), primary_key=True)
    subcategory_id: Mapped[int] = mapped_column(ForeignKey(ProductCategory.id, ondelete="CASCADE"), primary_key=True)
