from typing import Annotated

from asyncpg import Record
from everbase import Insert, Select, Update
from fastapi import APIRouter, Body, HTTPException

from core.models import Supplier
from core.objects import database
from core.utils.openapi import INTERNAL_ERROR_RESPONSE
from modules.v1.suppliers.schemes import (
    SupplierRead,
    SupplierCreate,
    SupplierCreateResponse,
    SupplierUpdate,
    SupplierIdType
)

SUPPLIER_NOT_FOUND_RESPONSE = {
    "description": "Поставщик не существует",
    "content": {
        "application/json": {
            "example": {"detail": "Поставщик не существует"}
        }
    }
}

router = APIRouter()


@router.post(
    "/",
    response_model=SupplierCreateResponse,
    status_code=201,
    summary="Создать нового поставщика",
    responses={
        201: {"description": "Идентификатор созданного поставщика"},
        500: INTERNAL_ERROR_RESPONSE,
    }
)
async def create_supplier(payload: Annotated[SupplierCreate, Body()]):
    async with database.get_connection() as connection:
        response: Record = await (
            Insert(Supplier)
            .values(**payload.model_dump())
            .returning(Supplier.id)
            .fetch_one(connection)
        )

    return {'id': response['id']}


@router.get(
    "/{supplier_id}",
    response_model=SupplierRead,
    summary="Получить информацию о поставщике",
    responses={
        200: {"description": "Информация о поставщике"},
        404: SUPPLIER_NOT_FOUND_RESPONSE,
        500: INTERNAL_ERROR_RESPONSE,
    }

)
async def get_supplier(supplier_id: SupplierIdType):
    async with database.get_connection() as connection:
        response = await (
            Select(
                Supplier.id,
                Supplier.name,
                Supplier.is_active,
                Supplier.created_at
            )
            .where(Supplier.id == supplier_id)
            .fetch_one(connection, model=SupplierRead)
        )

    if response is None:
        raise HTTPException(status_code=404, detail="Поставщик не существует")

    return response


@router.put(
    "/{supplier_id}",
    status_code=204,
    summary="Обновить информацию о поставщике",
    responses={
        204: {"description": "Поставщик успешно обновлён"},
        404: SUPPLIER_NOT_FOUND_RESPONSE,
        500: INTERNAL_ERROR_RESPONSE,
    }
)
async def update_supplier(
    supplier_id: SupplierIdType,
    payload: Annotated[SupplierUpdate, Body()]
):
    async with database.get_connection() as connection:
        response = await (
            Update(Supplier)
            .values(**payload.model_dump())
            .where(Supplier.id == supplier_id)
            .returning(Supplier.id)
            .fetch_one(connection)
        )

    if response is None:
        raise HTTPException(status_code=404, detail="Поставщика не существует")

    return None
