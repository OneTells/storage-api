from asyncpg import Record
from everbase import Connection
from sqlalchemy import Select, func

from core.models import Counterparty, CounterpartyRoleType


async def fetch_suppliers(
    connection: Connection,
    page: int,
    limit: int,
    is_active: bool | None = None
) -> list[Record]:
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
        .where(Counterparty.role == CounterpartyRoleType.SUPPLIER)
        .order_by(Counterparty.id)
        .offset((page - 1) * limit)
        .limit(limit)
    )

    if is_active is not None:
        query = query.where(Counterparty.is_active == is_active)

    return await connection.fetch(query)


async def count_suppliers(connection: Connection, is_active: bool | None = None) -> int:
    query = (
        Select(func.count(Counterparty.id))
        .where(Counterparty.role == CounterpartyRoleType.SUPPLIER)
    )

    if is_active is not None:
        query = query.where(Counterparty.is_active == is_active)

    return await connection.fetch_val(query)
