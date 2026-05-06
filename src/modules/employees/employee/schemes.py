from pydantic import BaseModel

from modules.employees.schemes import DefaultHourlyRateField, FullNameField, IdField, PositionField


class EmployeeCreate(BaseModel):
    full_name: FullNameField
    position: PositionField
    default_hourly_rate: DefaultHourlyRateField


class EmployeeCreateResponse(BaseModel):
    id: IdField


class EmployeeUpdate(BaseModel):
    full_name: FullNameField
    position: PositionField
    default_hourly_rate: DefaultHourlyRateField
