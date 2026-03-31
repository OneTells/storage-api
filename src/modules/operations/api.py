from datetime import datetime
from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Depends, Query

from core.methods import get_connection, require_permissions
from core.models import StockOperationType
from modules.object_units.object_unit.schemes import OperationsReadResponse
from modules.operations.inventory_adjustment.api import router as inventory_adjustment_router
from modules.operations.operation.api import router as operation_router

from modules.operations.production_output.api import router as production_output_router
from modules.operations.receipt.api import router as receipt_router
from modules.operations.reservation.api import router as reservation_router
from modules.operations.return_from_customer.api import router as return_from_customer_router
from modules.operations.return_from_production.api import router as return_from_production_router
from modules.operations.return_to_supplier.api import router as return_to_supplier_router
from modules.operations.shipment.api import router as shipment_router
from modules.operations.transfer.api import router as transfer_router
from modules.operations.write_off_to_production.api import router as write_off_to_production_router

router = APIRouter(prefix="/operations", tags=["Управление операциями"])
router.include_router(receipt_router)
router.include_router(shipment_router)
router.include_router(write_off_to_production_router)
router.include_router(production_output_router)
router.include_router(return_from_customer_router)
router.include_router(return_to_supplier_router)
router.include_router(return_from_production_router)
router.include_router(inventory_adjustment_router)
router.include_router(transfer_router)
router.include_router(reservation_router)
router.include_router(operation_router)


@router.get(
    "/",
    response_model=OperationsReadResponse,
    dependencies=[Depends(require_permissions("operations.read"))],
    summary="Получить список операций",
)
async def get_operations(
    connection: Annotated[Connection, Depends(get_connection)],
    page: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    limit: Annotated[int, Query(ge=1, le=1000, description="Количество элементов на странице")] = 100,
    operation_type: Annotated[StockOperationType | None, Query(description="Фильтр по типу операции")] = None,
    user_id: Annotated[int | None, Query(ge=1, description="Фильтр по пользователю")] = None,
    created_from: Annotated[datetime | None, Query(description="Начало периода создания операции")] = None,
    created_to: Annotated[datetime | None, Query(description="Конец периода создания операции")] = None,
):
    raise NotImplementedError
