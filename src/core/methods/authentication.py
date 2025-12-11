import hashlib
import hmac
from typing import Annotated

from asyncpg import Connection
from everbase import Select
from fastapi import HTTPException, Depends
from fastapi.security import APIKeyHeader

from core.config import settings
from core.models import UserSession, User
from core.schemas import UserModel, UserRole
from .database import get_connection


class Token:

    @staticmethod
    def get_signature(session_id: str, session_secret: str) -> str:
        return hmac.new(
            settings.secret_token.encode(),
            f"{session_id}.{session_secret}".encode(),
            hashlib.sha256,
        ).hexdigest()

    @staticmethod
    def validate(token: str) -> tuple[str, str]:
        try:
            session_id, signature = token.split(".", maxsplit=1)
        except ValueError:
            raise ValueError("Токен не валиден")

        return session_id, signature

    @classmethod
    def create(cls, session_id: str, session_secret: str) -> str:
        return f"{session_id}.{cls.get_signature(session_id, session_secret)}"


authorization_header = APIKeyHeader(name="authorization", auto_error=False)


class Authentication:

    def __init__(self, *, role: list[UserRole]):
        self.__role = role

    async def __call__(
        self,
        authorization: Annotated[str | None, Depends(authorization_header)],
        connection: Annotated[Connection, Depends(get_connection)],
    ) -> UserModel:
        if authorization is None:
            raise HTTPException(status_code=401, detail="Необходимо авторизоваться")

        try:
            scheme, token = authorization.split(" ", 1)
        except ValueError:
            raise HTTPException(status_code=403, detail="Токен не валиден")

        if scheme.lower() != "bearer":
            raise HTTPException(status_code=403, detail="Токен не валиден")

        try:
            session_id, signature = Token.validate(token)
        except ValueError:
            raise HTTPException(status_code=403, detail="Токен не валиден")

        response = await (
            Select(
                User.id,
                User.role,
                UserSession.id.label("session_id"),
                UserSession.secret,
                UserSession.is_active,
            )
            .join(UserSession, UserSession.user_id == User.id)
            .where(UserSession.id == session_id, User.is_active)
            .fetch_one(connection)
        )

        if response is None:
            raise HTTPException(status_code=403, detail="Токен не валиден")

        if not response["is_active"]:
            raise HTTPException(status_code=403, detail="Сессия не активна")

        if signature != Token.get_signature(response["session_id"], response["secret"]):
            raise HTTPException(status_code=403, detail="Токен не валиден")

        if response["role"] not in self.__role:
            raise HTTPException(status_code=403, detail="Недостаточно прав")

        return UserModel(**response)
