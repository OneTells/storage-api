from fastapi import APIRouter, Depends

from core.methods import get_current_user
# from modules.v1.catalog.api import router as catalog_router
# from modules.v1.arrivals.api import router as arrivals_router
# from modules.v1.categories.api import router as categories_router
# from modules.v1.object_units.api import router as object_units_router
# from modules.v1.objects.api import router as objects_router
# from modules.v1.reservations.api import router as reservations_router
# from modules.v1.sale_orders.api import router as sale_orders_router
# from modules.v1.suppliers.api import router as suppliers_router
# from modules.v1.transfers.api import router as transfers_router
from modules.warehouses.api import router as warehouses_router

main_router = APIRouter(prefix="/api/v1", dependencies=[Depends(get_current_user)])
# main_router.include_router(arrivals_router)

# main_router.include_router(object_units_router)
# main_router.include_router(objects_router)
# main_router.include_router(reservations_router)
# main_router.include_router(sale_orders_router)

# main_router.include_router(transfers_router)
# main_router.include_router(write_offs_router)

main_router.include_router(warehouses_router)
# main_router.include_router(suppliers_router)
# main_router.include_router(categories_router)
# main_router.include_router(catalog_router)
