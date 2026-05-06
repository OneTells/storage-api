from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path

from core.exceptions import APIException
from core.methods import get_connection, require_permissions
from modules.employees.employee import repositories
from modules.employees.employee.responses import EMPLOYEE_NOT_FOUND
from modules.employees.employee.schemes import EmployeeCreate, EmployeeCreateResponse, EmployeeUpdate
from modules.employees.schemes import EmployeeRead

router = APIRouter()


@router.post(
    "/",
    response_model=EmployeeCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions('employee.create'))],
    summary="Создать нового сотрудника"
)
async def create_employee(
    connection: Annotated[Connection, Depends(get_connection)],
    payload: Annotated[EmployeeCreate, Body()]
):
    employee_id = await repositories.create_employee(connection, payload)
    return EmployeeCreateResponse(id=employee_id)


@router.get(
    "/{employee_id}",
    response_model=EmployeeRead,
    dependencies=[Depends(require_permissions('employee.read'))],
    summary="Получить информацию о сотруднике",
    responses={
        404: EMPLOYEE_NOT_FOUND
    }
)
async def get_employee(
    connection: Annotated[Connection, Depends(get_connection)],
    employee_id: Annotated[int, Path(ge=1, description="Идентификатор сотрудника")]
):
    employee = await repositories.get_employee_by_id(connection, employee_id)

    if employee is None:
        raise APIException(
            status_code=404,
            code="EMPLOYEE_NOT_FOUND",
            message="Сотрудник не найден"
        )

    return EmployeeRead(**employee)


@router.put(
    "/{employee_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('employee.update'))],
    summary="Обновить информацию о сотруднике",
    responses={
        404: EMPLOYEE_NOT_FOUND
    }
)
async def update_employee(
    connection: Annotated[Connection, Depends(get_connection)],
    employee_id: Annotated[int, Path(ge=1, description="Идентификатор сотрудника")],
    payload: Annotated[EmployeeUpdate, Body()]
):
    employee = await repositories.get_employee_by_id(connection, employee_id)

    if employee is None:
        raise APIException(
            status_code=404,
            code="EMPLOYEE_NOT_FOUND",
            message="Сотрудник не найден"
        )

    await repositories.update_employee(connection, employee_id, payload)
