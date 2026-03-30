from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path

from core.methods import get_connection, require_permissions
from modules.suppliers.schemes import SupplierRead
from modules.suppliers.supplier.responses import SUPPLIER_NOT_FOUND
from modules.suppliers.supplier.schemes import SupplierCreate, SupplierCreateResponse, SupplierUpdate

router = APIRouter()


@router.post(
    "/",
    response_model=SupplierCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions('supplier.create'))],
    summary="Создать нового поставщика",
    responses={
        201: {"description": "Поставщик успешно создан"},
    }
)
async def create_supplier(
    connection: Annotated[Connection, Depends(get_connection)],
    payload: Annotated[SupplierCreate, Body()]
):
    raise NotImplementedError


@router.get(
    "/{supplier_id}",
    response_model=SupplierRead,
    dependencies=[Depends(require_permissions('supplier.read'))],
    summary="Получить информацию о поставщике",
    responses={
        200: {"description": "Информация о поставщике успешно получена"},
        404: SUPPLIER_NOT_FOUND,
    }
)
async def get_supplier(
    connection: Annotated[Connection, Depends(get_connection)],
    supplier_id: Annotated[int, Path(ge=1, description="Идентификатор поставщика")]
):
    raise NotImplementedError


@router.put(
    "/{supplier_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('supplier.update'))],
    summary="Обновить информацию о поставщике",
    responses={
        204: {"description": "Поставщик успешно обновлён"},
        404: SUPPLIER_NOT_FOUND,
    }
)
async def update_supplier(
    connection: Annotated[Connection, Depends(get_connection)],
    supplier_id: Annotated[int, Path(ge=1, description="Идентификатор поставщика")],
    payload: Annotated[SupplierUpdate, Body()]
):
    raise NotImplementedError
