from everbase import Database

from core.config import settings

database = Database(
    settings.database_dsn.encoded_string(),
    min_size=settings.database_pool_size,
    max_size=settings.database_pool_size
)
