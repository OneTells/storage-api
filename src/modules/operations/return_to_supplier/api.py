from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends

from core.methods import get_connection, get_current_user, require_permissions
from core.schemes import UserModel
from modules.operations.return_to_supplier.responses import RETURN_TO_SUPPLIER_404
from modules.operations.return_to_supplier.schemes import ReturnToSupplierCreate
from modules.operations.schemes import OperationCreateResponse

router = APIRouter()


@router.post(
    "/return_to_supplier",
    response_model=OperationCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions("operations.return_to_supplier.create"))],
    summary="Возврат поставщику",
    responses={
        404: RETURN_TO_SUPPLIER_404
    }
)
async def create_return_to_supplier(
    connection: Annotated[Connection, Depends(get_connection)],
    user: Annotated[UserModel, Depends(get_current_user)],
    payload: Annotated[ReturnToSupplierCreate, Body()],
):
    raise NotImplementedError

