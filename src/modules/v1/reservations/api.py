from typing import Annotated

from asyncpg import Connection
from fastapi import APIRouter, Depends

from core.methods import get_connection
from .reservation.api import router as reservation_router

router = APIRouter(prefix="/reservations")
router.include_router(reservation_router)

