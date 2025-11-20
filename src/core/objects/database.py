from everbase import DatabasePool

from core.config import settings

database = DatabasePool(settings.database_dsn)
