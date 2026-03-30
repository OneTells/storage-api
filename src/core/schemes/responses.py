from typing import Annotated, Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    detail: Annotated[Any, Field(description="Детали ошибки")]


UNAUTHORIZED_RESPONSE = {
    'description': 'Неавторизованный доступ',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'examples': {
                'unauthorized': {
                    'summary': 'Нет или неверная аутентификация',
                    'value': {
                        'detail': 'Требуется аутентификация'
                    },
                },
                'invalid_token': {
                    'summary': 'Токен не валиден',
                    'value': {
                        'detail': 'Невалидный токен'
                    },
                },
                'session_inactive': {
                    'summary': 'Сессия не активна',
                    'value': {
                        'detail': 'Сессия не активна'
                    },
                },
                'session_not_found': {
                    'summary': 'Сессия не существует',
                    'value': {
                        'detail': 'Сессия не существует'
                    },
                },
            }
        }
    },
}

FORBIDDEN_RESPONSE = {
    'description': 'Доступ запрещён',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'examples': {
                'insufficient_permissions': {
                    'summary': 'Недостаточно прав',
                    'value': {
                        'detail': 'Недостаточно прав для выполнения действия'
                    },
                },
                'user_banned': {
                    'summary': 'Пользователь заблокирован',
                    'value': {
                        'detail': 'Пользователь заблокирован'
                    },
                },
            }
        }
    },
}

INTERNAL_ERROR_RESPONSE = {
    'description': 'Внутренняя ошибка сервера',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'example': {
                'detail': 'Внутренняя ошибка сервера'
            },
        }
    },
}
