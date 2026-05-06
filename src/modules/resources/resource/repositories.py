from asyncpg import Record
from everbase import Connection
from sqlalchemy import Select, Update
from sqlalchemy.dialects.postgresql import Insert

from core.models import Resource
from modules.resources.resource.schemes import ResourceCreate, ResourceUpdate


async def create_resource(connection: Connection, payload: ResourceCreate) -> int:
    query = (
        Insert(Resource)
        .values(**payload.model_dump())
        .returning(Resource.id)
    )

    return await connection.fetch_val(query)


async def get_resource_by_id(connection: Connection, resource_id: int) -> Record | None:
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
        .where(Resource.id == resource_id)
    )

    return await connection.fetch_row(query)


async def update_resource(connection: Connection, resource_id: int, payload: ResourceUpdate) -> None:
    query = (
        Update(Resource)
        .values(**payload.model_dump())
        .where(Resource.id == resource_id)
    )

    await connection.execute(query)
