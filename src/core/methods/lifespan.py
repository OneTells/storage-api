import os
from contextlib import asynccontextmanager
from sys import stderr
from typing import Any, AsyncIterator

from fastapi import FastAPI
from loguru import logger

from core.objects.database import database


class Lifespan:

    @staticmethod
    async def __on_startup() -> None:
        logger.remove()
        logger.add(stderr, level="INFO", backtrace=True, diagnose=True)

        log_dir = "/app/memory/logs"

        os.makedirs(log_dir, exist_ok=True)

        logger.add(
             f"{log_dir}/info.log",
            level="INFO",
            diagnose=False,
            enqueue=False,
            compression="tar.xz",
            retention="10 days",
            rotation="100 MB",
        )
        logger.add(
            f"{log_dir}/debug.log",
            level="DEBUG",
            diagnose=False,
            enqueue=False,
            compression="tar.xz",
            retention="10 days",
            rotation="100 MB",
        )

        await database.connect()

        logger.info("API запушен")

    @staticmethod
    async def __on_shutdown() -> None:
        await database.close()

        logger.info("API остановлен")

    @classmethod
    @asynccontextmanager
    async def run(cls, _: FastAPI) -> AsyncIterator[Any]:
        await cls.__on_startup()
        yield
        await cls.__on_shutdown()
