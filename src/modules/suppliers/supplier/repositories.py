from asyncpg import Record
from everbase import Connection
from sqlalchemy import Select, Update
from sqlalchemy.dialects.postgresql import Insert

from core.models import Counterparty, CounterpartyRoleType
from modules.suppliers.supplier.schemes import SupplierCreate, SupplierUpdate


async def create_supplier(connection: Connection, payload: SupplierCreate) -> int:
    query = (
        Insert(Counterparty)
        .values(role=CounterpartyRoleType.SUPPLIER, **payload.model_dump())
        .returning(Counterparty.id)
    )

    return await connection.fetch_val(query)


async def get_supplier_by_id(connection: Connection, supplier_id: int) -> Record | None:
    query = (
        Select(
            Counterparty.id,
            Counterparty.type,
            Counterparty.name,
            Counterparty.phone,
            Counterparty.email,
            Counterparty.comment,
            Counterparty.inn,
            Counterparty.kpp,
            Counterparty.ogrn,
            Counterparty.legal_address,
            Counterparty.director,
            Counterparty.director_position,
            Counterparty.is_active,
            Counterparty.created_at
        )
        .where(
            Counterparty.id == supplier_id,
            Counterparty.role == CounterpartyRoleType.SUPPLIER
        )
    )

    return await connection.fetch_row(query)


async def exist_supplier_by_name(connection: Connection, name: str) -> bool:
    query = (
        Select(
            Select(1)
            .select_from(Counterparty)
            .where(
                Counterparty.role == CounterpartyRoleType.SUPPLIER,
                Counterparty.name == name
            )
            .exists()
        )
    )
    return await connection.fetch_val(query)


async def update_supplier(connection: Connection, supplier_id: int, payload: SupplierUpdate) -> None:
    query = (
        Update(Counterparty)
        .values(**payload.model_dump())
        .where(
            Counterparty.id == supplier_id,
            Counterparty.role == CounterpartyRoleType.SUPPLIER
        )
    )

    await connection.execute(query)
