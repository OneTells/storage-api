from fastapi import APIRouter

from modules.products.catalog.api import router as products_catalog_router
from modules.products.categories.api import router as products_categories_router
from modules.products.product.api import router as product_router

router = APIRouter(prefix="/products", tags=["Продукты"])
router.include_router(products_catalog_router)
router.include_router(products_categories_router)
router.include_router(product_router)
