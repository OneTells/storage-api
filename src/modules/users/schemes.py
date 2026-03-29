from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field

from core.schemes import Pagination

IdField = Annotated[int, Field(ge=1, description="Идентификатор пользователя")]
NameField = Annotated[str, Field(min_length=1, max_length=255, description="Имя пользователя")]
UsernameField = Annotated[str, Field(min_length=3, max_length=50, description="Имя пользователя (логин)")]
PasswordField = Annotated[str, Field(min_length=8, max_length=128, description="Пароль пользователя")]
IsActiveField = Annotated[bool, Field(description="Флаг активности пользователя")]
CreatedAtField = Annotated[AwareDatetime, Field(description="Время создания пользователя")]


class UserRead(BaseModel):
    id: IdField
    name: NameField
    username: UsernameField
    is_active: IsActiveField
    created_at: CreatedAtField


class UsersReadResponse(BaseModel):
    users: list[UserRead]
    pagination: Pagination
