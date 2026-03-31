from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends

from core.methods import get_connection, get_current_user, require_permissions
from core.schemes import UserModel
from modules.operations.inventory_adjustment.responses import INVENTORY_ADJUSTMENT_404
from modules.operations.inventory_adjustment.schemes import InventoryAdjustmentCreate
from modules.operations.schemes import OperationCreateResponse

router = APIRouter()


@router.post(
    "/inventory_adjustment",
    response_model=OperationCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions("operations.inventory_adjustment.create"))],
    summary="Инвентаризация",
    responses={
        404: INVENTORY_ADJUSTMENT_404
    }
)
async def create_inventory_adjustment(
    connection: Annotated[Connection, Depends(get_connection)],
    user: Annotated[UserModel, Depends(get_current_user)],
    payload: Annotated[InventoryAdjustmentCreate, Body()],
):
    raise NotImplementedError

