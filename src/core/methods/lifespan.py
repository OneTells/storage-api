from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from loguru import logger

from core.config import complete_logging, configure_logging
from core.objects.database import database


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    await database.connect()

    logger.info("API запушен")
    yield
    logger.info("API остановлен")

    await database.close()
    await complete_logging()
