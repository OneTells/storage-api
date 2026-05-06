from core.schemes import ErrorResponse

USER_LOGIN_CONFLICT = {
    "description": "Пользователь с таким логином уже существует",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": "USER_USERNAME_EXISTS",
                "message": "Пользователь с таким именем уже существует",
                "details": {}
            }
        }
    }
}

SESSION_NOT_FOUND = {
    "description": "Сессия не найдена или уже завершена",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": "SESSION_NOT_FOUND",
                "message": "Сессия не найдена или уже завершена",
                "details": {}
            }
        }
    }
}
