from typing import Annotated

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    detail: Annotated[str, Field(description="Описание ошибки")]


UNAUTHORIZED_RESPONSE = {
    "description": "Неавторизованный доступ",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "detail": "Неавторизованный доступ"
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
                    "value": {"detail": "Токен не валиден"}
                },
                "user_banned": {
                    "summary": "Пользователь заблокирован",
                    "value": {"detail": "Пользователь заблокирован"}
                },
                "session_inactive": {
                    "summary": "Сессия не активна",
                    "value": {"detail": "Сессия не активна"}
                },
                "not_found_session": {
                    "summary": "Сессия не существует",
                    "value": {"detail": "Сессия не существует"}
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
                "detail": "Необрабатываемая сущность"
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
                "detail": "Внутренняя ошибка сервера"
            }
        }
    }
}
