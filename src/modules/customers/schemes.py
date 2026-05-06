from typing import Annotated, Literal

from pydantic import AwareDatetime, BaseModel, Field, TypeAdapter

from core.models import CounterpartyType
from core.schemes import Pagination

IdField = Annotated[int, Field(ge=1, description="Идентификатор клиента")]
NameField = Annotated[str, Field(min_length=1, max_length=200, description="Название клиента")]
TypeField = Annotated[CounterpartyType, Field(description="Тип контрагента")]
PhoneField = Annotated[str | None, Field(default=None, max_length=50, description="Телефон")]
EmailField = Annotated[str | None, Field(default=None, max_length=255, description="Email")]
CommentField = Annotated[str, Field(min_length=1, max_length=2000, description="Комментарий")]
InnField = Annotated[str | None, Field(default=None, max_length=20, description="ИНН")]
KppField = Annotated[str | None, Field(default=None, max_length=20, description="КПП")]
OgrnField = Annotated[str | None, Field(default=None, max_length=20, description="ОГРН/ОГРНИП")]
LegalAddressField = Annotated[str | None, Field(default=None, max_length=500, description="Юридический адрес")]
DirectorField = Annotated[str | None, Field(default=None, max_length=255, description="ФИО руководителя")]
DirectorPositionField = Annotated[str | None, Field(default=None, max_length=255, description="Должность руководителя")]
IsActiveField = Annotated[bool, Field(description="Флаг активности клиента")]
CreatedAtField = Annotated[AwareDatetime, Field(description="Время создания клиента")]


class CustomerReadBase(BaseModel):
    type: TypeField

    id: IdField
    name: NameField
    phone: PhoneField
    email: EmailField
    comment: CommentField
    is_active: IsActiveField
    created_at: CreatedAtField


class CustomerReadIndividual(CustomerReadBase):
    type: Literal[CounterpartyType.INDIVIDUAL]


class CustomerReadEntrepreneur(CustomerReadBase):
    type: Literal[CounterpartyType.ENTREPRENEUR]

    inn: InnField
    ogrn: OgrnField
    legal_address: LegalAddressField


class CustomerReadLegalEntity(CustomerReadBase):
    type: Literal[CounterpartyType.LEGAL_ENTITY]

    inn: InnField
    kpp: KppField
    ogrn: OgrnField
    legal_address: LegalAddressField
    director: DirectorField
    director_position: DirectorPositionField


CustomerRead = Annotated[
    CustomerReadIndividual |
    CustomerReadEntrepreneur |
    CustomerReadLegalEntity,
    Field(discriminator="type")
]

customer_read_adapter = TypeAdapter(CustomerRead)


class CustomersReadResponse(BaseModel):
    customers: list[CustomerRead]
    pagination: Pagination
