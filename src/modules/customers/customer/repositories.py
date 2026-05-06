from asyncpg import Record
from everbase import Connection
from sqlalchemy import Select, Update
from sqlalchemy.dialects.postgresql import Insert

from core.models import Counterparty, CounterpartyRoleType
from modules.customers.customer.schemes import CustomerCreate, CustomerUpdate


async def create_customer(connection: Connection, payload: CustomerCreate) -> int:
    query = (
        Insert(Counterparty)
        .values(role=CounterpartyRoleType.CUSTOMER, **payload.model_dump())
        .returning(Counterparty.id)
    )

    return await connection.fetch_val(query)


async def get_customer_by_id(connection: Connection, customer_id: int) -> Record | None:
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
            Counterparty.id == customer_id,
            Counterparty.role == CounterpartyRoleType.CUSTOMER
        )
    )

    return await connection.fetch_row(query)


async def exist_customer_by_name(connection: Connection, name: str) -> bool:
    query = (
        Select(
            Select(1)
            .select_from(Counterparty)
            .where(
                Counterparty.role == CounterpartyRoleType.CUSTOMER,
                Counterparty.name == name
            )
            .exists()
        )
    )
    return await connection.fetch_val(query)


async def update_customer(connection: Connection, customer_id: int, payload: CustomerUpdate) -> None:
    query = (
        Update(Counterparty)
        .values(**payload.model_dump())
        .where(
            Counterparty.id == customer_id,
            Counterparty.role == CounterpartyRoleType.CUSTOMER
        )
    )

    await connection.execute(query)
