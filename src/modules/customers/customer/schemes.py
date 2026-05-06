from typing import Annotated, Literal

from pydantic import BaseModel, Field

from core.models import CounterpartyType
from modules.customers.schemes import (
    CommentField, DirectorField, DirectorPositionField, EmailField, IdField, InnField, IsActiveField, KppField,
    LegalAddressField, NameField, OgrnField, PhoneField
)


class CustomerBasePayload(BaseModel):
    name: NameField
    phone: PhoneField
    email: EmailField
    comment: CommentField
    is_active: IsActiveField


class CustomerIndividualPayload(CustomerBasePayload):
    type: Literal[CounterpartyType.INDIVIDUAL]


class CustomerEntrepreneurPayload(CustomerBasePayload):
    type: Literal[CounterpartyType.ENTREPRENEUR]

    inn: InnField
    ogrn: OgrnField
    legal_address: LegalAddressField


class CustomerLegalEntityPayload(CustomerBasePayload):
    type: Literal[CounterpartyType.LEGAL_ENTITY]

    inn: InnField
    kpp: KppField
    ogrn: OgrnField
    legal_address: LegalAddressField
    director: DirectorField
    director_position: DirectorPositionField


CustomerCreate = Annotated[
    CustomerIndividualPayload |
    CustomerEntrepreneurPayload |
    CustomerLegalEntityPayload,
    Field(discriminator="type")
]


class CustomerCreateResponse(BaseModel):
    id: IdField


CustomerUpdate = Annotated[
    CustomerIndividualPayload |
    CustomerEntrepreneurPayload |
    CustomerLegalEntityPayload,
    Field(discriminator="type")
]
