from fastapi import APIRouter

from .object_unit.api import router as object_unit_router

router = APIRouter(prefix="/object_units")
router.include_router(object_unit_router)
