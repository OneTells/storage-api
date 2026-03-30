from enum import auto, StrEnum
from typing import Annotated, Any

from pydantic import BaseModel, Field


class ErrorCode(StrEnum):
    # auth / access
    UNAUTHORIZED = auto()
    INSUFFICIENT_PERMISSIONS = auto()
    INVALID_CREDENTIALS = auto()
    INVALID_TOKEN = auto()
    USER_BANNED = auto()
    SESSION_INACTIVE = auto()
    SESSION_NOT_FOUND = auto()

    # category
    CATEGORY_NOT_FOUND = auto()

    CUSTOMER_NOT_FOUND = auto()

    OBJECT_UNIT_NOT_FOUND = auto()

    OBJECT_NOT_FOUND = auto()
    OBJECT_HAS_RELATIONS = auto()

    PERMISSION_NOT_FOUND = auto()
    PERMISSION_NAME_ALREADY_EXISTS = auto()
    PERMISSION_CODENAME_ALREADY_EXISTS = auto()

    ROLE_NOT_FOUND = auto()
    ROLE_ALREADY_EXISTS = auto()

    SUPPLIER_NOT_FOUND = auto()

    USER_NOT_FOUND = auto()
    USER_LOGIN_ALREADY_EXISTS = auto()
    USER_OR_ROLE_NOT_FOUND = auto()

    WAREHOUSE_NOT_FOUND = auto()

    # client errors
    UNPROCESSABLE_ENTITY = auto()

    # server
    INTERNAL_ERROR = auto()


ERROR_CODE_HTTP_STATUS = {
    # auth / access - 401 Unauthorized
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.INVALID_CREDENTIALS: 401,
    ErrorCode.INVALID_TOKEN: 401,
    ErrorCode.SESSION_INACTIVE: 401,
    ErrorCode.SESSION_NOT_FOUND: 401,

    # auth / access - 403 Forbidden
    ErrorCode.INSUFFICIENT_PERMISSIONS: 403,
    ErrorCode.USER_BANNED: 403,

    # entities - 404 Not Found
    ErrorCode.CATEGORY_NOT_FOUND: 404,
    ErrorCode.CUSTOMER_NOT_FOUND: 404,
    ErrorCode.OBJECT_UNIT_NOT_FOUND: 404,
    ErrorCode.OBJECT_NOT_FOUND: 404,
    ErrorCode.PERMISSION_NOT_FOUND: 404,
    ErrorCode.ROLE_NOT_FOUND: 404,
    ErrorCode.SUPPLIER_NOT_FOUND: 404,
    ErrorCode.USER_NOT_FOUND: 404,
    ErrorCode.USER_OR_ROLE_NOT_FOUND: 404,
    ErrorCode.WAREHOUSE_NOT_FOUND: 404,

    # entities - 409 Conflict
    ErrorCode.PERMISSION_NAME_ALREADY_EXISTS: 409,
    ErrorCode.PERMISSION_CODENAME_ALREADY_EXISTS: 409,
    ErrorCode.ROLE_ALREADY_EXISTS: 409,
    ErrorCode.USER_LOGIN_ALREADY_EXISTS: 409,
    ErrorCode.OBJECT_HAS_RELATIONS: 409,

    # client errors - 422 Unprocessable Entity
    ErrorCode.UNPROCESSABLE_ENTITY: 422,

    # server - 500 Internal Server Error
    ErrorCode.INTERNAL_ERROR: 500,
}


class ErrorResponse(BaseModel):
    error_code: ErrorCode
    description: Annotated[str, Field(min_length=1, max_length=255)]
    params: dict[str, Any] | None = None


UNAUTHORIZED_RESPONSE = {
    "description": "Неавторизованный доступ",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": ErrorCode.UNAUTHORIZED,
                "message": "Неавторизованный доступ",
                "params": {}
            }
        }
    }
}

FORBIDDEN_RESPONSE = {
    "description": "Доступ запрещен",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "invalid_token": {
                    "summary": "Токен не валиден",
                    "value": {
                        "code": ErrorCode.INVALID_TOKEN,
                        "message": "Токен не валиден",
                        "params": {}
                    }
                },
                "user_banned": {
                    "summary": "Пользователь заблокирован",
                    "value": {
                        "code": ErrorCode.USER_BANNED,
                        "message": "Пользователь заблокирован",
                        "params": {}
                    }
                },
                "session_inactive": {
                    "summary": "Сессия не активна",
                    "value": {
                        "code": ErrorCode.SESSION_INACTIVE,
                        "message": "Сессия не активна",
                        "params": {}
                    }
                },
                "not_found_session": {
                    "summary": 'Сессия не существует',
                    "value": {
                        "code": ErrorCode.SESSION_NOT_FOUND,
                        "message": "Сессия не существует",
                        "params": {}
                    }
                }
            }
        }
    }
}

UNPROCESSABLE_ENTITY_RESPONSE = {
    "description": "Необрабатываемая сущность",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": ErrorCode.UNPROCESSABLE_ENTITY,
                "message": "Необрабатываемая сущность",
                "params": {}
            }
        }
    }
}

INTERNAL_ERROR_RESPONSE = {
    "description": "Внутренняя ошибка сервера",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": ErrorCode.INTERNAL_ERROR,
                "message": "Внутренняя ошибка сервера",
                "params": {}
            }
        }
    }
}
