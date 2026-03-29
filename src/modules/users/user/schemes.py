from pydantic import BaseModel

from modules.users.schemes import IsActiveField, NameField, PasswordField, UsernameField


class UserCreate(BaseModel):
    name: NameField
    username: UsernameField
    password: PasswordField
    is_active: IsActiveField


class UserCreateResponse(BaseModel):
    id: int


class UserUpdate(BaseModel):
    name: NameField
    username: UsernameField
    password: PasswordField
    is_active: IsActiveField
