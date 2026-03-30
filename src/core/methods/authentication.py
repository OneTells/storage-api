import hashlib
import hmac
from typing import Annotated, Awaitable, Callable

from everbase import Connection
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import ARRAY, func, Select, Text

from core.config import settings
from core.methods import get_connection
from core.models import Permission, Role, RolePermission, User, UserRole, UserSession
from core.schemes import UserModel


class Token:
    SEPARATOR = "."

    @staticmethod
    def _create_token_signature(session_id: int, secret: str) -> str:
        return hmac.new(secret.encode(), str(session_id).encode(), hashlib.sha256).hexdigest()

    @classmethod
    def generate(cls, session_id: int, secret: str) -> str:
        signature = cls._create_token_signature(session_id, secret)
        return f"{session_id}{cls.SEPARATOR}{signature}"

    @classmethod
    def parse(cls, token: str, secret: str) -> int:
        try:
            session_id_str, signature = token.split(cls.SEPARATOR, maxsplit=1)
            session_id = int(session_id_str)
        except (ValueError, IndexError):
            raise ValueError

        expected_signature = cls._create_token_signature(session_id, secret)

        if not hmac.compare_digest(signature, expected_signature):
            raise ValueError

        return session_id


async def _validate_session(connection: Connection, session_id: int) -> UserModel:
    user_info = await connection.fetch_row(
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

    if user_info is None:
        raise HTTPException(status_code=401, detail='Сессия не существует')

    if not user_info['user_active']:
        raise HTTPException(status_code=403, detail='Пользователь заблокирован')

    if not user_info['session_active']:
        raise HTTPException(status_code=401, detail='Сессия не активна')

    return UserModel(id=user_info['id'], permissions=user_info['permissions'])


async def get_current_user(
    connection: Annotated[Connection, Depends(get_connection)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(HTTPBearer(auto_error=False))]
) -> UserModel:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail='Требуется аутентификация',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    try:
        session_id = Token.parse(credentials.credentials, settings.secret_token)
    except ValueError:
        raise HTTPException(status_code=401, detail='Невалидный токен')

    return await _validate_session(connection, session_id)


def require_permissions(*required_permissions: str) -> Callable[..., Awaitable[None]]:

    async def dependency(user: Annotated[UserModel, Depends(get_current_user)]) -> None:
        if any(x for x in required_permissions if x not in user.permissions):
            raise HTTPException(status_code=403, detail='Недостаточно прав для выполнения действия')

        return None

    return dependency
