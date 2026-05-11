import asyncio
import sys
from typing import TYPE_CHECKING

from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter
from aiogram.types import LinkPreviewOptions
from loguru import logger

from core.config import settings
from core.objects import bot

if TYPE_CHECKING:
    from loguru import Message


class TelegramHandler:
    MAX_MESSAGE_LENGTH = 4096

    def __init__(self, chat_id: str | int, max_retries: int = 5) -> None:
        self._chat_id = chat_id
        self._max_retries = max_retries

        self._lock = asyncio.Lock()

    async def __call__(self, message: Message) -> None:
        if len(message) > self.MAX_MESSAGE_LENGTH:
            message = message[:self.MAX_MESSAGE_LENGTH]

        async with self._lock:
            for _ in range(self._max_retries):
                try:
                    await bot.send_message(
                        chat_id=self._chat_id,
                        text=message,
                        link_preview_options=LinkPreviewOptions(
                            is_disabled=True
                        )
                    )
                    return
                except TelegramRetryAfter as e:
                    await asyncio.sleep(e.retry_after)
                except TelegramAPIError:
                    pass


LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS Z}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | {extra} - <level>{message}</level>"
)


def configure_logging() -> None:
    logger.remove()

    logger.add(
        sys.stderr,
        format=LOG_FORMAT,
        level='DEBUG',
        diagnose=False
    )

    # logger.add(
    #     TelegramHandler(settings.telegram_log_chat_id),
    #     level="WARNING",
    #     format=lambda record: "Уровень: {level}\nСообщение: {message}".format(**record),
    #     diagnose=False
    # )


async def complete_logging() -> None:
    await logger.complete()
    logger.remove()
