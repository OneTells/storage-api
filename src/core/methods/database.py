from typing import Any, AsyncGenerator

from asyncpg import Connection

from core.objects import database


async def get_connection() -> AsyncGenerator[Connection, Any]:
    async with database.get_connection() as connection:
        yield connection
