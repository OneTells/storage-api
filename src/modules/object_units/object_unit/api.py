from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Depends, Path, Query

from core.methods import get_connection, require_permissions
from core.schemes import ErrorResponse
from modules.object_units.object_unit.schemes import OperationsReadResponse

OBJECT_UNIT_NOT_FOUND_RESPONSE = {
    "description": "Единица объекта не найдена",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {"detail": "Единица объекта не найдена"}
        }
    }
}

router = APIRouter()


@router.get(
    '/{object_unit_id}/operations',
    response_model=OperationsReadResponse,
    dependencies=[Depends(require_permissions('operations.read'))],
    summary="Получить операции для единицы объекта",
    responses={
        200: {"description": "Список операций успешно получен"},
        404: OBJECT_UNIT_NOT_FOUND_RESPONSE,
    }
)
async def get_operations(
    connection: Annotated[Connection, Depends(get_connection)],
    object_unit_id: Annotated[int, Path(ge=1, description="Идентификатор единицы объекта")],
    page: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    limit: Annotated[int, Query(ge=1, le=1000, description="Количество элементов на странице")] = 100,
):
    raise NotImplementedError
