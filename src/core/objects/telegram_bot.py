from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession

from core.config import settings

bot = Bot(
    token=settings.telegram_token,
    session=AiohttpSession(proxy=settings.telegram_bot_proxy),
    default=DefaultBotProperties(parse_mode='HTML')
)
