from fastapi import APIRouter

from modules.materials.catalog.api import router as materials_catalog_router
from modules.materials.categories.api import router as materials_categories_router
from modules.materials.material.api import router as material_router

router = APIRouter(prefix="/materials", tags=["Управление материалами"])
router.include_router(materials_catalog_router)
router.include_router(materials_categories_router)
router.include_router(material_router)
