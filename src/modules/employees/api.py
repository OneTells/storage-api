from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Depends, Query

from core.methods import get_connection, require_permissions
from core.schemes import Pagination
from modules.employees import repositories
from modules.employees.employee.api import router as employee_router
from modules.employees.schemes import EmployeeRead, EmployeesReadResponse

router = APIRouter(prefix="/employees", tags=["Управление сотрудниками"])
router.include_router(employee_router)


@router.get(
    "/",
    response_model=EmployeesReadResponse,
    dependencies=[Depends(require_permissions('employees.read'))],
    summary="Получить список сотрудников"
)
async def get_employees(
    connection: Annotated[Connection, Depends(get_connection)],
    page: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    limit: Annotated[int, Query(ge=1, le=1000, description="Количество элементов на странице")] = 100
):
    employees = await repositories.fetch_employees(connection, page, limit)
    total = await repositories.count_employees(connection)

    return EmployeesReadResponse(
        employees=[EmployeeRead(**x) for x in employees],
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            pages=(total + limit - 1) // limit,
            has_next=page * limit < total,
            has_prev=page > 1
        )
    )
