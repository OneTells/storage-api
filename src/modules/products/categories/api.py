from fastapi import APIRouter

from modules.products.categories.category.api import router as product_category_router

router = APIRouter(prefix="/categories")
router.include_router(product_category_router)
