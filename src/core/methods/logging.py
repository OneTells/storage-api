import os
import sys

from loguru import logger


def configure_logging() -> None:
    log_dir = "/app/memory/logs"

    logger.remove()
    logger.add(
        sys.stderr,
        format=(
            '<green>{time:YYYY-MM-DD HH:mm:ss.SSSS}</green> '
            '| <level>{level: <8}</level> '
            '| <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> '
            '- <level>{message}</level>'
        ),
        level='INFO',
        enqueue=False,
        diagnose=False
    )

    os.makedirs(log_dir, exist_ok=True)

    logger.add(
        f"{log_dir}/info.log",
        level="INFO",
        enqueue=False,
        diagnose=False,
        compression="tar.xz",
        retention="10 days",
        rotation="100 MB",
    )

    logger.add(
        f"{log_dir}/debug.log",
        level="DEBUG",
        enqueue=False,
        diagnose=False,
        compression="tar.xz",
        retention="10 days",
        rotation="100 MB",
    )


async def complete_logging():
    await logger.complete()
    logger.remove()
