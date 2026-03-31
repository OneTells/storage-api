from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends

from core.methods import get_connection, get_current_user, require_permissions
from core.schemes import UserModel
from modules.operations.schemes import OperationCreateResponse
from modules.operations.write_off_to_production.responses import WRITE_OFF_TO_PRODUCTION_404
from modules.operations.write_off_to_production.schemes import WriteOffToProductionCreate

router = APIRouter()


@router.post(
    "/write_off_to_production",
    response_model=OperationCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions("operations.write_off_to_production.create"))],
    summary="Списание в производство",
    responses={
        404: WRITE_OFF_TO_PRODUCTION_404
    }
)
async def create_write_off_to_production(
    connection: Annotated[Connection, Depends(get_connection)],
    user: Annotated[UserModel, Depends(get_current_user)],
    payload: Annotated[WriteOffToProductionCreate, Body()],
):
    raise NotImplementedError

