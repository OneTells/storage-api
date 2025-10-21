from pydantic import BaseModel, AwareDatetime


class WarehouseModel(BaseModel):
    id: int

    name: str
    address: str
    is_active: bool

    created_at: AwareDatetime
