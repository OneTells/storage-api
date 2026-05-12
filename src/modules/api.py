from fastapi import APIRouter, Depends

from core.methods import get_current_user
from core.schemes import FORBIDDEN_RESPONSE, UNAUTHORIZED_RESPONSE
from modules.auth.api import router as auth_module_router
from modules.customers.api import router as customers_router
from modules.employees.api import router as employees_router
from modules.materials.api import router as materials_router
from modules.operations.api import router as operations_router
from modules.permissions.api import router as permissions_router
from modules.products.api import router as products_router
from modules.production_orders.api import router as production_orders_router
from modules.resources.api import router as resources_router
from modules.roles.api import router as roles_router
from modules.suppliers.api import router as suppliers_router
from modules.units.api import router as units_router
from modules.users.api import router as users_router
from modules.warehouses.api import router as warehouses_router

router_with_auth = APIRouter(
    dependencies=[Depends(get_current_user)],
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: FORBIDDEN_RESPONSE,
    }
)
router_with_auth.include_router(permissions_router)
router_with_auth.include_router(roles_router)
router_with_auth.include_router(customers_router)
router_with_auth.include_router(employees_router)
router_with_auth.include_router(materials_router)
router_with_auth.include_router(operations_router)
router_with_auth.include_router(production_orders_router)
router_with_auth.include_router(products_router)
router_with_auth.include_router(resources_router)
router_with_auth.include_router(suppliers_router)
router_with_auth.include_router(units_router)
router_with_auth.include_router(users_router)
router_with_auth.include_router(warehouses_router)

main_router = APIRouter(prefix="/api/v1")
main_router.include_router(auth_module_router)
main_router.include_router(router_with_auth)
