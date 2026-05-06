from asyncpg import Record
from everbase import Connection
from sqlalchemy import Select, Update
from sqlalchemy.dialects.postgresql import Insert

from core.models import Employee
from modules.employees.employee.schemes import EmployeeCreate, EmployeeUpdate


async def create_employee(connection: Connection, payload: EmployeeCreate) -> int:
    query = (
        Insert(Employee)
        .values(**payload.model_dump())
        .returning(Employee.id)
    )

    return await connection.fetch_val(query)


async def get_employee_by_id(connection: Connection, employee_id: int) -> Record | None:
    query = (
        Select(
            Employee.id,
            Employee.full_name,
            Employee.position,
            Employee.default_hourly_rate,
            Employee.created_at
        )
        .where(Employee.id == employee_id)
    )

    return await connection.fetch_row(query)


async def update_employee(connection: Connection, employee_id: int, payload: EmployeeUpdate) -> None:
    query = (
        Update(Employee)
        .values(**payload.model_dump())
        .where(Employee.id == employee_id)
    )

    await connection.execute(query)
