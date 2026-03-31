from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends

from core.methods import get_connection, get_current_user, require_permissions
from core.schemes import UserModel
from modules.operations.receipt.responses import RECEIPT_404
from modules.operations.receipt.schemes import ReceiptCreate
from modules.operations.schemes import OperationCreateResponse

router = APIRouter()


@router.post(
    "/receipt",
    response_model=OperationCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions('operations.receipt.create'))],
    summary="Приёмка от поставщика",
    responses={
        404: RECEIPT_404
    }
)
async def create_receipt(
    connection: Annotated[Connection, Depends(get_connection)],
    user: Annotated[UserModel, Depends(get_current_user)],
    payload: Annotated[ReceiptCreate, Body()]
):
    raise NotImplementedError
