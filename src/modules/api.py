from fastapi import APIRouter

from modules.v1.api import v1_router

main_router = APIRouter(prefix="/api")
main_router.include_router(v1_router)
