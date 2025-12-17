from fastapi import APIRouter

from modules.v1.catalog.api import router as catalog_router
# from modules.v1.arrivals.api import router as arrivals_router
from modules.v1.categories.api import router as categories_router
# from modules.v1.object_units.api import router as object_units_router
# from modules.v1.objects.api import router as objects_router
# from modules.v1.reservations.api import router as reservations_router
# from modules.v1.sale_orders.api import router as sale_orders_router
from modules.v1.suppliers.api import router as suppliers_router
# from modules.v1.transfers.api import router as transfers_router
from modules.v1.warehouses.api import router as warehouses_router

# from modules.v1.write_offs.api import router as write_offs_router

v1_router = APIRouter(prefix="/v1")
# v1_router.include_router(arrivals_router)

# v1_router.include_router(object_units_router)
# v1_router.include_router(objects_router)
# v1_router.include_router(reservations_router)
# v1_router.include_router(sale_orders_router)

# v1_router.include_router(transfers_router)
# v1_router.include_router(write_offs_router)

v1_router.include_router(warehouses_router)
# v1_router.include_router(suppliers_router)
# v1_router.include_router(categories_router)
# v1_router.include_router(catalog_router)
