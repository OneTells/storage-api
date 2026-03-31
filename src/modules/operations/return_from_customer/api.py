from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends

from core.methods import get_connection, get_current_user, require_permissions
from core.schemes import UserModel
from modules.operations.return_from_customer.responses import RETURN_FROM_CUSTOMER_404
from modules.operations.return_from_customer.schemes import ReturnFromCustomerCreate
from modules.operations.schemes import OperationCreateResponse

router = APIRouter()


@router.post(
    "/return_from_customer",
    response_model=OperationCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions("operations.return_from_customer.create"))],
    summary="Возврат от клиента",
    responses={
        404: RETURN_FROM_CUSTOMER_404
    }
)
async def create_return_from_customer(
    connection: Annotated[Connection, Depends(get_connection)],
    user: Annotated[UserModel, Depends(get_current_user)],
    payload: Annotated[ReturnFromCustomerCreate, Body()],
):
    raise NotImplementedError

