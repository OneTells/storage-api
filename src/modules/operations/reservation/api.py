from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends

from core.methods import get_connection, get_current_user, require_permissions
from core.schemes import UserModel
from modules.operations.reservation.responses import RESERVATION_404
from modules.operations.reservation.schemes import ReservationCreate
from modules.operations.schemes import OperationCreateResponse

router = APIRouter()


@router.post(
    "/reservation",
    response_model=OperationCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions("operations.reservation.create"))],
    summary="Бронирование",
    responses={
        404: RESERVATION_404
    }
)
async def create_reservation(
    connection: Annotated[Connection, Depends(get_connection)],
    user: Annotated[UserModel, Depends(get_current_user)],
    payload: Annotated[ReservationCreate, Body()],
):
    raise NotImplementedError


@router.delete(
    "/reservation",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions("operations.reservation.cancel"))],
    summary="Отмена бронирования",
    responses={
        404: RESERVATION_404
    }
)
async def cancel_reservation(
    connection: Annotated[Connection, Depends(get_connection)],
    user: Annotated[UserModel, Depends(get_current_user)],
    operation_id: Annotated[int, Body(ge=1, description="Идентификатор операции бронирования")],
):
    raise NotImplementedError
