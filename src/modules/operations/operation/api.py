from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Depends, Path

from core.methods import get_connection, require_permissions
from modules.object_units.object_unit.schemes import OperationType
from modules.operations.operation.responses import OPERATION_NOT_FOUND

router = APIRouter()


@router.get(
    "/{operation_id}",
    response_model=OperationType,
    dependencies=[Depends(require_permissions("operations.read"))],
    summary="Получить операцию",
    responses={
        404: OPERATION_NOT_FOUND
    }
)
async def get_operation(
    connection: Annotated[Connection, Depends(get_connection)],
    operation_id: Annotated[int, Path(ge=1, description="Идентификатор операции")],
):
    raise NotImplementedError
