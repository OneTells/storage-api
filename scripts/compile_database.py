from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import CreateEnumType
from sqlalchemy.dialects.postgresql.asyncpg import dialect
from sqlalchemy.sql.ddl import CreateTable

from core.models import (
    CounterpartyRoleType, CounterpartyType, OperationStatus, ProductionOrderStatus, ReceiptStatus, ReservationStatus,
    ResourceType, StockOperationType, UnitCategoryEnum
)
from core.models.base import Base


def main() -> None:
    current_dialect = dialect()
    end = '\n;'

    # Генерация SQL для всех enum
    enums = [
        UnitCategoryEnum,
        OperationStatus,
        ReceiptStatus,
        ReservationStatus,
        ProductionOrderStatus,
        CounterpartyRoleType,
        CounterpartyType,
        ResourceType,
        StockOperationType
    ]

    for enum_type in enums:
        print(CreateEnumType(Enum(enum_type)).compile(dialect=current_dialect), end=end)

    # Генерация SQL для всех таблиц
    for table in Base.metadata.tables.values():
        print(CreateTable(table).compile(dialect=current_dialect), end=end)


if __name__ == '__main__':
    main()
