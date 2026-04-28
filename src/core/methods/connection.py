from functools import wraps
from typing import Any, AsyncGenerator, Callable

from asyncpg.pool import PoolConnectionProxy
from asyncpg.transaction import Transaction
from everbase import Connection
from everbase.database import PoolAcquireContextWrapper

from core.objects import database


class _LazyTransaction:

    def __init__(self, lazy_conn: _LazyConnection, **kwargs: Any) -> None:
        self._lazy_conn = lazy_conn
        self._kwargs = kwargs

        self._transaction: Transaction | None = None

    async def __aenter__(self) -> None:
        if self._transaction is not None:
            return

        real_conn = await self._lazy_conn.acquire()
        self._transaction = real_conn.transaction(**self._kwargs)
        await self._transaction.__aenter__()  # type: ignore

    async def __aexit__(self, *args, **kwargs) -> None:
        if self._transaction is None:
            return

        await self._transaction.__aexit__(*args, **kwargs)


class _LazyConnection:

    def __init__(self, acquire_func: Callable[[], PoolAcquireContextWrapper]) -> None:
        self._acquire_func = acquire_func

        self._pool_connection_wrapper: PoolAcquireContextWrapper | None = None
        self._connection: Connection | None = None

    async def acquire(self) -> Connection:
        if self._connection is None:
            self._pool_connection_wrapper = self._acquire_func()
            self._connection = await self._pool_connection_wrapper.__aenter__()  # type: ignore

        return self._connection  # type: ignore

    async def release(self) -> None:
        if self._connection is None or self._pool_connection_wrapper is None:
            return

        await self._pool_connection_wrapper.__aexit__(None, None, None)

        self._pool_connection_wrapper = None
        self._connection = None

    # --- Свойства и методы, соответствующие интерфейсу ConnectionWrapper ---

    @property
    def value(self) -> PoolConnectionProxy:
        if self._connection is None:
            raise RuntimeError(
                "Connection has not been acquired yet. "
                "Call an async method (e.g., execute, fetch, transaction) first."
            )

        return self._connection.value

    def transaction(self, **kwargs: Any) -> _LazyTransaction:
        return _LazyTransaction(self, **kwargs)

    def __getattr__(self, name: str) -> Any:
        original_method: Callable[..., Any] | None = getattr(Connection, name, None)

        if original_method is None:
            raise AttributeError(f"'{Connection.__name__}' has no attribute '{name}'")

        @wraps(original_method)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            connection = await self.acquire()
            return await getattr(connection, name)(*args, **kwargs)

        return wrapper


async def get_connection() -> AsyncGenerator[Connection, None]:
    lazy = _LazyConnection(database.acquire)

    try:
        yield lazy  # type: ignore
    finally:
        await lazy.release()
