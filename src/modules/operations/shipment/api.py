from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends

from core.methods import get_connection, get_current_user, require_permissions
from core.schemes import UserModel
from modules.operations.schemes import OperationCreateResponse
from modules.operations.shipment.responses import SHIPMENT_404
from modules.operations.shipment.schemes import ShipmentCreate

router = APIRouter()


@router.post(
    "/shipment",
    response_model=OperationCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions("operations.shipment.create"))],
    summary="Отгрузка",
    responses={
        404: SHIPMENT_404
    }
)
async def create_shipment(
    connection: Annotated[Connection, Depends(get_connection)],
    user: Annotated[UserModel, Depends(get_current_user)],
    payload: Annotated[ShipmentCreate, Body()],
):
    raise NotImplementedError

