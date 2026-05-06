from decimal import Decimal
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field

from core.schemes import Pagination

IdField = Annotated[int, Field(ge=1, description="Идентификатор сотрудника")]
FullNameField = Annotated[str, Field(min_length=1, max_length=255, description="ФИО сотрудника")]
PositionField = Annotated[str | None, Field(default=None, max_length=255, description="Должность сотрудника")]
DefaultHourlyRateField = Annotated[
    Decimal,
    Field(ge=0, max_digits=10, decimal_places=2, description="Базовая почасовая ставка сотрудника")
]
CreatedAtField = Annotated[AwareDatetime, Field(description="Время добавления сотрудника")]


class EmployeeRead(BaseModel):
    id: IdField
    full_name: FullNameField
    position: PositionField
    default_hourly_rate: DefaultHourlyRateField
    created_at: CreatedAtField


class EmployeesReadResponse(BaseModel):
    employees: list[EmployeeRead]
    pagination: Pagination
