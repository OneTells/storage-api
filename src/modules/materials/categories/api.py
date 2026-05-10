from fastapi import APIRouter

from modules.materials.categories.category.api import router as category_router

router = APIRouter(prefix="/categories")
router.include_router(category_router)
