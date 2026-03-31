from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends

from core.methods import get_connection, get_current_user, require_permissions
from core.schemes import UserModel
from modules.operations.production_output.responses import PRODUCTION_OUTPUT_404
from modules.operations.production_output.schemes import ProductionOutputCreate
from modules.operations.schemes import OperationCreateResponse

router = APIRouter()


@router.post(
    "/production_output",
    response_model=OperationCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions("operations.production_output.create"))],
    summary="Выпуск продукции",
    responses={404: PRODUCTION_OUTPUT_404},
)
async def create_production_output(
    connection: Annotated[Connection, Depends(get_connection)],
    user: Annotated[UserModel, Depends(get_current_user)],
    payload: Annotated[ProductionOutputCreate, Body()],
):
    raise NotImplementedError

