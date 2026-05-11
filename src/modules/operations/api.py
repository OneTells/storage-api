from fastapi import APIRouter

from modules.operations.inventory_adjustment.api import router as inventory_adjustment_router
from modules.operations.production_output.api import router as production_output_router
from modules.operations.receipt.api import router as receipt_router
from modules.operations.reservation.api import router as reservation_router
from modules.operations.shipment.api import router as shipment_router
from modules.operations.transfer.api import router as transfer_router
from modules.operations.write_off.api import router as write_off_router
from modules.operations.write_off_to_production.api import router as write_off_to_production_router

router = APIRouter(prefix="/operations", tags=["Управление операциями"])
router.include_router(receipt_router)
router.include_router(shipment_router)
router.include_router(production_output_router)
router.include_router(write_off_to_production_router)
router.include_router(write_off_router)
router.include_router(inventory_adjustment_router)
router.include_router(transfer_router)
router.include_router(reservation_router)
