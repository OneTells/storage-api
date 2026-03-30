from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path

from core.methods import get_connection, require_permissions
from core.schemes import ErrorCode, ErrorResponse
from modules.customers.customer.schemes import CustomerCreate, CustomerCreateResponse, CustomerUpdate
from modules.customers.schemes import CustomerRead

router = APIRouter()


@router.post(
    "/",
    response_model=CustomerCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions('customer.create'))],
    summary="Создать нового клиента",
    responses={
        201: {"description": "Клиент успешно создан"},
    }
)
async def create_customer(
    connection: Annotated[Connection, Depends(get_connection)],
    payload: Annotated[CustomerCreate, Body()]
):
    raise NotImplementedError


@router.get(
    "/{customer_id}",
    response_model=CustomerRead,
    dependencies=[Depends(require_permissions('customer.read'))],
    summary="Получить информацию о клиенте",
    responses={
        200: {"description": "Информация о клиенте успешно получена"},
        404: {
            "description": "Клиент не найден",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "code": ErrorCode.CUSTOMER_NOT_FOUND,
                        "message": "Клиент не найден",
                        "params": {}
                    }
                }
            }
        },
    }
)
async def get_customer(
    connection: Annotated[Connection, Depends(get_connection)],
    customer_id: Annotated[int, Path(ge=1, description="Идентификатор клиента")]
):
    raise NotImplementedError


@router.put(
    "/{customer_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('customer.update'))],
    summary="Обновить информацию о клиенте",
    responses={
        204: {"description": "Клиент успешно обновлён"},
        404: {
            "description": "Клиент не найден",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "code": ErrorCode.CUSTOMER_NOT_FOUND,
                        "message": "Клиент не найден",
                        "params": {}
                    }
                }
            }
        },
    }
)
async def update_customer(
    connection: Annotated[Connection, Depends(get_connection)],
    customer_id: Annotated[int, Path(ge=1, description="Идентификатор клиента")],
    payload: Annotated[CustomerUpdate, Body()]
):
    raise NotImplementedError
