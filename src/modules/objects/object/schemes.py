from pydantic import BaseModel

from modules.objects.schemes import DescriptionField, IdField, IsActiveField, NameField


class ObjectCreate(BaseModel):
    name: NameField
    description: DescriptionField
    is_active: IsActiveField


class ObjectCreateResponse(BaseModel):
    id: IdField


class ObjectUpdate(BaseModel):
    name: NameField
    description: DescriptionField
    is_active: IsActiveField
