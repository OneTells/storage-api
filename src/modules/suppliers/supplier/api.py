from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path

from core.exceptions import APIException
from core.methods import get_connection, require_permissions
from modules.suppliers.schemes import supplier_read_adapter, SupplierRead
from modules.suppliers.supplier import repositories
from modules.suppliers.supplier.responses import SUPPLIER_NAME_CONFLICT, SUPPLIER_NOT_FOUND
from modules.suppliers.supplier.schemes import SupplierCreate, SupplierCreateResponse, SupplierUpdate

router = APIRouter()


@router.post(
    "/",
    response_model=SupplierCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions('supplier.create'))],
    summary="Создать нового поставщика",
    responses={
        409: SUPPLIER_NAME_CONFLICT
    }
)
async def create_supplier(
    connection: Annotated[Connection, Depends(get_connection)],
    payload: Annotated[SupplierCreate, Body()]
):
    supplier_exists = await repositories.exist_supplier_by_name(connection, payload.name)

    if supplier_exists:
        raise APIException(
            status_code=409,
            code="SUPPLIER_NAME_EXISTS",
            message="Поставщик с таким названием уже существует"
        )

    supplier_id = await repositories.create_supplier(connection, payload)
    return SupplierCreateResponse(id=supplier_id)


@router.get(
    "/{supplier_id}",
    response_model=SupplierRead,
    dependencies=[Depends(require_permissions('supplier.read'))],
    summary="Получить информацию о поставщике",
    responses={
        404: SUPPLIER_NOT_FOUND
    }
)
async def get_supplier(
    connection: Annotated[Connection, Depends(get_connection)],
    supplier_id: Annotated[int, Path(ge=1, description="Идентификатор поставщика")]
):
    supplier = await repositories.get_supplier_by_id(connection, supplier_id)

    if supplier is None:
        raise APIException(
            status_code=404,
            code="SUPPLIER_NOT_FOUND",
            message="Поставщик не найден"
        )

    return supplier_read_adapter.validate_python(dict(supplier))


@router.put(
    "/{supplier_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('supplier.update'))],
    summary="Обновить информацию о поставщике",
    responses={
        404: SUPPLIER_NOT_FOUND,
        409: SUPPLIER_NAME_CONFLICT,
    }
)
async def update_supplier(
    connection: Annotated[Connection, Depends(get_connection)],
    supplier_id: Annotated[int, Path(ge=1, description="Идентификатор поставщика")],
    payload: Annotated[SupplierUpdate, Body()]
):
    supplier = await repositories.get_supplier_by_id(connection, supplier_id)

    if supplier is None:
        raise APIException(
            status_code=404,
            code="SUPPLIER_NOT_FOUND",
            message="Поставщик не найден"
        )

    current_name = supplier["name"]

    if current_name != payload.name:
        duplicated_name = await repositories.exist_supplier_by_name(connection, payload.name)

        if duplicated_name:
            raise APIException(
                status_code=409,
                code="SUPPLIER_NAME_EXISTS",
                message="Поставщик с таким названием уже существует"
            )

    await repositories.update_supplier(connection, supplier_id, payload)
