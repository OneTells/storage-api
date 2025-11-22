from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import FastAPI
from loguru import logger

from .logging import configure_logging, complete_logging
from core.objects.database import database


class Lifespan:

    @staticmethod
    async def _startup() -> None:
        configure_logging()
        await database.connect()
        logger.info("API запушен")

    @staticmethod
    async def _shutdown() -> None:
        await database.close()
        logger.info("API остановлен")
        await complete_logging()

    @classmethod
    @asynccontextmanager
    async def run(cls, _: FastAPI) -> AsyncIterator[Any]:
        await cls._startup()
        yield
        await cls._shutdown()
