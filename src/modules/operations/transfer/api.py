from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends

from core.methods import get_connection, get_current_user, require_permissions
from core.schemes import UserModel
from modules.operations.schemes import OperationCreateResponse
from modules.operations.transfer.responses import TRANSFER_404
from modules.operations.transfer.schemes import TransferCreate

router = APIRouter()


@router.post(
    "/transfer",
    response_model=OperationCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions("operations.transfer.create"))],
    summary="Перемещение",
    responses={404: TRANSFER_404},
)
async def create_transfer(
    connection: Annotated[Connection, Depends(get_connection)],
    user: Annotated[UserModel, Depends(get_current_user)],
    payload: Annotated[TransferCreate, Body()],
):
    raise NotImplementedError

