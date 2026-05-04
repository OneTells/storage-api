import hashlib
import hmac
from typing import Annotated, Awaitable, Callable
from uuid import UUID

from asyncpg import Record
from everbase import Connection
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials as AuthCredentials, HTTPBearer
from sqlalchemy import ARRAY, func, Select, Text

from core.config import settings
from core.exceptions import APIException
from core.models import Permission, Role, RolePermission, User, UserRole, UserSession
from core.schemes import UserModel
from .connection import get_connection


class Token:
    _SEPARATOR = "."

    @staticmethod
    def _create_token_signature(session_id: UUID, secret: str) -> str:
        return hmac.new(secret.encode(), str(session_id).encode(), hashlib.sha256).hexdigest()

    @classmethod
    def generate(cls, session_id: UUID, secret: str) -> str:
        signature = cls._create_token_signature(session_id, secret)
        return f"{session_id}{cls._SEPARATOR}{signature}"

    @classmethod
    def parse(cls, token: str, secret: str) -> UUID:
        try:
            session_id_str, signature = token.split(cls._SEPARATOR, maxsplit=1)
            session_id = UUID(session_id_str)
        except (ValueError, IndexError):
            raise ValueError

        expected_signature = cls._create_token_signature(session_id, secret)

        if not hmac.compare_digest(signature, expected_signature):
            raise ValueError

        return session_id


async def _get_user_info_by_session_id(connection: Connection, session_id: UUID) -> Record | None:
    query = (
        Select(
            User.id,
            UserSession.is_active.label("session_active"),
            User.is_active.label("user_active"),
            func.coalesce(func.array_agg(func.distinct(Permission.codename), type_=ARRAY(Text)), []).label("permissions")
        )
        .join(User, UserSession.user_id == User.id)
        .outerjoin(UserRole, User.id == UserRole.user_id)
        .outerjoin(Role, UserRole.role_id == Role.id)
        .outerjoin(RolePermission, Role.id == RolePermission.role_id)
        .outerjoin(Permission, RolePermission.permission_id == Permission.id)
        .where(UserSession.id == session_id)
        .group_by(User.id, UserSession.is_active, User.is_active)
    )

    return await connection.fetch_row(query)


async def get_current_user_optional(
    connection: Annotated[Connection, Depends(get_connection)],
    auth_credentials: Annotated[AuthCredentials | None, Depends(HTTPBearer(auto_error=False))]
) -> UserModel | None:
    if auth_credentials is None:
        return None

    try:
        session_id = Token.parse(auth_credentials.credentials, settings.secret_token)
    except ValueError:
        raise APIException(
            status_code=403,
            code="INVALID_TOKEN",
            message="Токен не валиден",
        )

    user_info = await _get_user_info_by_session_id(connection, session_id)

    if user_info is None:
        raise APIException(
            status_code=403,
            code="SESSION_NOT_FOUND",
            message="Сессия не существует"
        )

    if not user_info['user_active']:
        raise APIException(
            status_code=403,
            code="USER_BANNED",
            message="Пользователь заблокирован"
        )

    if not user_info['session_active']:
        raise APIException(
            status_code=403,
            code="SESSION_INACTIVE",
            message="Сессия не активна"
        )

    return UserModel(id=user_info['id'], permissions=user_info['permissions'])


async def get_current_user(user: Annotated[UserModel | None, Depends(get_current_user_optional)]) -> UserModel:
    if user is None:
        raise APIException(
            status_code=401,
            code="UNAUTHORIZED",
            message="Требуется аутентификация",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user


def require_permissions(*required_permissions: str) -> Callable[..., Awaitable[None]]:

    async def dependency(user: Annotated[UserModel, Depends(get_current_user)]) -> None:
        if any(x for x in required_permissions if x not in user.permissions):
            raise APIException(
                status_code=403,
                code="INSUFFICIENT_PERMISSIONS",
                message="Недостаточно прав"
            )

        return None

    return dependency
