from typing import Annotated

from pydantic import BaseModel, Field

UsernameField = Annotated[str, Field(min_length=3, max_length=50, description="Имя пользователя (логин)")]
PasswordField = Annotated[str, Field(min_length=8, max_length=128, description="Пароль пользователя")]


class AuthPayload(BaseModel):
    username: UsernameField
    password: PasswordField
