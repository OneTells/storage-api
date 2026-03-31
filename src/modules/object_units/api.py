from fastapi import APIRouter

from modules.object_units.object_unit.api import router as object_unit_router

router = APIRouter(prefix="/object-units", tags=["Управление юнитами объектов"])
router.include_router(object_unit_router)
