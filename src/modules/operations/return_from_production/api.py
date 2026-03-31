from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends

from core.methods import get_connection, get_current_user, require_permissions
from core.schemes import UserModel
from modules.operations.return_from_production.responses import RETURN_FROM_PRODUCTION_404
from modules.operations.return_from_production.schemes import ReturnFromProductionCreate
from modules.operations.schemes import OperationCreateResponse

router = APIRouter()


@router.post(
    "/return_from_production",
    response_model=OperationCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions("operations.return_from_production.create"))],
    summary="Возврат из производства",
    responses={
        404: RETURN_FROM_PRODUCTION_404
    }
)
async def create_return_from_production(
    connection: Annotated[Connection, Depends(get_connection)],
    user: Annotated[UserModel, Depends(get_current_user)],
    payload: Annotated[ReturnFromProductionCreate, Body()],
):
    raise NotImplementedError

