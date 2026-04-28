
from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import CreateEnumType
from sqlalchemy.dialects.postgresql.asyncpg import dialect
from sqlalchemy.sql.ddl import CreateTable

from core.models import *
from core.models.base import Base


def main() -> None:
    current_dialect = dialect()
    end = '\n;'

    print(CreateEnumType(Enum(ObjectUnitStatus)).compile(dialect=current_dialect), end=end)
    print(CreateEnumType(Enum(StockOperationType)).compile(dialect=current_dialect), end=end)

    for table in Base.metadata.tables.values():
        print(CreateTable(table).compile(dialect=current_dialect), end=end)


if __name__ == '__main__':
    main()
