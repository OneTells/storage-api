from asyncpg import Record
from everbase import Connection
from sqlalchemy import func, Select

from core.models import Resource, ResourceType


async def fetch_resources(
    connection: Connection,
    page: int,
    limit: int,
    resource_type: ResourceType | None = None
) -> list[Record]:
    query = (
        Select(
            Resource.id,
            Resource.type,
            Resource.name,
            Resource.unit_id,
            Resource.fixed_rate,
            Resource.initial_amount,
            Resource.service_life,
            Resource.created_at
        )
        .order_by(Resource.id)
        .offset((page - 1) * limit)
        .limit(limit)
    )

    if resource_type is not None:
        query = query.where(Resource.type == resource_type)

    return await connection.fetch(query)


async def count_resources(connection: Connection, resource_type: ResourceType | None = None) -> int:
    query = Select(func.count(Resource.id))

    if resource_type is not None:
        query = query.where(Resource.type == resource_type)

    return await connection.fetch_val(query)
