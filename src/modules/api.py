from fastapi import APIRouter, Depends

from core.methods import get_current_user
from modules.auth.api import router as auth_module_router
from modules.customers.api import router as customers_router
from modules.object_units.api import router as object_units_router
from modules.objects.api import router as objects_router
from modules.operations.api import router as operations_router
from modules.permissions.api import router as permissions_router
from modules.roles.api import router as roles_router
from modules.suppliers.api import router as suppliers_router
from modules.users.api import router as users_router
from modules.warehouses.api import router as warehouses_router

main_router = APIRouter(prefix="/api/v1")
main_router.include_router(auth_module_router)
main_router.include_router(customers_router, dependencies=[Depends(get_current_user)])
main_router.include_router(object_units_router, dependencies=[Depends(get_current_user)])
main_router.include_router(objects_router, dependencies=[Depends(get_current_user)])
main_router.include_router(operations_router, dependencies=[Depends(get_current_user)])
main_router.include_router(permissions_router, dependencies=[Depends(get_current_user)])
main_router.include_router(roles_router, dependencies=[Depends(get_current_user)])
main_router.include_router(suppliers_router, dependencies=[Depends(get_current_user)])
main_router.include_router(users_router, dependencies=[Depends(get_current_user)])
main_router.include_router(warehouses_router, dependencies=[Depends(get_current_user)])
