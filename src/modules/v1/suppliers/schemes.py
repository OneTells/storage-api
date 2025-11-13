from pydantic import BaseModel, AwareDatetime


class SupplierModel(BaseModel):
    id: int

    name: str
    is_active: bool

    created_at: AwareDatetime
