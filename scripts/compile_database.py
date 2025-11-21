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


def main():
    print(CreateEnumType(Enum(UserRole)).compile(dialect=dialect()))
    print(CreateEnumType(Enum(ArrivalStatus)).compile(dialect=dialect()))
    print(CreateEnumType(Enum(TransferStatus)).compile(dialect=dialect()))
    print(CreateEnumType(Enum(ObjectUnitStatus)).compile(dialect=dialect()))
    print(CreateEnumType(Enum(SaleOrderStatus)).compile(dialect=dialect()))
    print(CreateEnumType(Enum(WriteOffStatus)).compile(dialect=dialect()))

    for k, v in Base.metadata.tables.items():
        print(CreateTable(v).compile(dialect=dialect()))


if __name__ == '__main__':
    main()
