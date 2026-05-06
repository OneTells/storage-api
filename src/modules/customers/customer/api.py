from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path

from core.exceptions import APIException
from core.methods import get_connection, require_permissions
from modules.customers.customer import repositories
from modules.customers.customer.responses import CUSTOMER_NAME_CONFLICT, CUSTOMER_NOT_FOUND
from modules.customers.customer.schemes import CustomerCreate, CustomerCreateResponse, CustomerUpdate
from modules.customers.schemes import CustomerRead, customer_read_adapter

router = APIRouter()


@router.post(
    "/",
    response_model=CustomerCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions('customer.create'))],
    summary="Создать нового клиента",
    responses={
        409: CUSTOMER_NAME_CONFLICT
    }
)
async def create_customer(
    connection: Annotated[Connection, Depends(get_connection)],
    payload: Annotated[CustomerCreate, Body()]
):
    customer_exists = await repositories.exist_customer_by_name(connection, payload.name)

    if customer_exists:
        raise APIException(
            status_code=409,
            code="CUSTOMER_NAME_EXISTS",
            message="Клиент с таким названием уже существует"
        )

    customer_id = await repositories.create_customer(connection, payload)
    return CustomerCreateResponse(id=customer_id)


@router.get(
    "/{customer_id}",
    response_model=CustomerRead,
    dependencies=[Depends(require_permissions('customer.read'))],
    summary="Получить информацию о клиенте",
    responses={
        404: CUSTOMER_NOT_FOUND
    }
)
async def get_customer(
    connection: Annotated[Connection, Depends(get_connection)],
    customer_id: Annotated[int, Path(ge=1, description="Идентификатор клиента")]
):
    customer = await repositories.get_customer_by_id(connection, customer_id)

    if customer is None:
        raise APIException(
            status_code=404,
            code="CUSTOMER_NOT_FOUND",
            message="Клиент не найден"
        )

    return customer_read_adapter.validate_python(dict(customer))


@router.put(
    "/{customer_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('customer.update'))],
    summary="Обновить информацию о клиенте",
    responses={
        404: CUSTOMER_NOT_FOUND,
        409: CUSTOMER_NAME_CONFLICT,
    }
)
async def update_customer(
    connection: Annotated[Connection, Depends(get_connection)],
    customer_id: Annotated[int, Path(ge=1, description="Идентификатор клиента")],
    payload: Annotated[CustomerUpdate, Body()]
):
    customer = await repositories.get_customer_by_id(connection, customer_id)

    if customer is None:
        raise APIException(
            status_code=404,
            code="CUSTOMER_NOT_FOUND",
            message="Клиент не найден"
        )

    if customer["name"] != payload.name:
        duplicated_name = await repositories.exist_customer_by_name(connection, payload.name)

        if duplicated_name:
            raise APIException(
                status_code=409,
                code="CUSTOMER_NAME_EXISTS",
                message="Клиент с таким названием уже существует"
            )

    await repositories.update_customer(connection, customer_id, payload)
