from everbase import Base
from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import dialect, CreateEnumType
from sqlalchemy.sql.ddl import CreateTable

from core.models import *
from core.models.arrivals import ArrivalStatus
from core.models.object_units import ObjectUnitStatus
from core.models.sale_orders import SaleOrderStatus
from core.models.transfers import TransferStatus
from core.models.write_offs import WriteOffStatus
from core.schemes import UserRole


def main() -> None:
    current_dialect = dialect()
    end = '\n;'

    print(CreateEnumType(Enum(UserRole)).compile(dialect=current_dialect), end=end)
    print(CreateEnumType(Enum(ArrivalStatus)).compile(dialect=current_dialect), end=end)
    print(CreateEnumType(Enum(TransferStatus)).compile(dialect=current_dialect), end=end)
    print(CreateEnumType(Enum(ObjectUnitStatus)).compile(dialect=current_dialect), end=end)
    print(CreateEnumType(Enum(SaleOrderStatus)).compile(dialect=current_dialect), end=end)
    print(CreateEnumType(Enum(WriteOffStatus)).compile(dialect=current_dialect), end=end)

    for table in Base.metadata.tables.values():
        print(CreateTable(table).compile(dialect=current_dialect), end=end)


if __name__ == '__main__':
    main()
