from typing import Annotated, Any

from pydantic import BaseModel, Field


class ErrorResponse[DetailsT: Any = dict](BaseModel):
    code: Annotated[str, Field(description="Код ошибки")]
    message: Annotated[str, Field(description="Описание ошибки")]
    details: Annotated[DetailsT, Field(description="Детали ошибки")]


UNAUTHORIZED_RESPONSE = {
    "description": "Неавторизованный доступ",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": "UNAUTHORIZED",
                "message": "Требуется аутентификация",
                "details": {}
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
                        "code": "INVALID_TOKEN",
                        "message": "Токен не валиден",
                        "details": {}
                    }
                },
                "user_banned": {
                    "summary": "Пользователь заблокирован",
                    "value": {
                        "code": "USER_BANNED",
                        "message": "Пользователь заблокирован",
                        "details": {}
                    }
                },
                "session_inactive": {
                    "summary": "Сессия не активна",
                    "value": {
                        "code": "SESSION_INACTIVE",
                        "message": "Сессия не активна",
                        "details": {}
                    }
                },
                "not_found_session": {
                    "summary": "Сессия не существует",
                    "value": {
                        "code": "SESSION_NOT_FOUND",
                        "message": "Сессия не существует",
                        "details": {}
                    }
                },
                "insufficient_permissions": {
                    "summary": "Недостаточно прав",
                    "value": {
                        "code": "INSUFFICIENT_PERMISSIONS",
                        "message": "Недостаточно прав",
                        "details": {}
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
                "code": "UNPROCESSABLE_ENTITY",
                "message": "Необрабатываемая сущность",
                "details": {}
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
                "code": "INTERNAL_ERROR",
                "message": "Внутренняя ошибка сервера",
                "details": {}
            }
        }
    }
}
