from typing import Annotated, Literal

from pydantic import BaseModel, Field

from core.models import CounterpartyType
from modules.suppliers.schemes import (
    CommentField, DirectorField, DirectorPositionField, EmailField, IdField, InnField, IsActiveField, KppField,
    LegalAddressField, NameField, OgrnField, PhoneField
)


class SupplierBasePayload(BaseModel):
    name: NameField
    phone: PhoneField
    email: EmailField
    comment: CommentField
    is_active: IsActiveField


class SupplierIndividualPayload(SupplierBasePayload):
    type: Literal[CounterpartyType.INDIVIDUAL]


class SupplierEntrepreneurPayload(SupplierBasePayload):
    type: Literal[CounterpartyType.ENTREPRENEUR]

    inn: InnField
    ogrn: OgrnField
    legal_address: LegalAddressField


class SupplierLegalEntityPayload(SupplierBasePayload):
    type: Literal[CounterpartyType.LEGAL_ENTITY]

    inn: InnField
    kpp: KppField
    ogrn: OgrnField
    legal_address: LegalAddressField
    director: DirectorField
    director_position: DirectorPositionField


SupplierCreate = Annotated[
    SupplierIndividualPayload |
    SupplierEntrepreneurPayload |
    SupplierLegalEntityPayload,
    Field(discriminator="type")
]


class SupplierCreateResponse(BaseModel):
    id: IdField


SupplierUpdate = Annotated[
    SupplierIndividualPayload |
    SupplierEntrepreneurPayload |
    SupplierLegalEntityPayload,
    Field(discriminator="type")
]
