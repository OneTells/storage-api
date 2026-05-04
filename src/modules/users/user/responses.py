from core.schemes import ErrorResponse

USER_ROLE_404 = {
    "description": "Пользователь или роль не найдены",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "user_not_found": {
                    "summary": "Пользователь не найден",
                    "value": {
                        "code": "USER_NOT_FOUND",
                        "message": "Пользователь не найден",
                        "details": {}
                    }
                },
                "role_not_found": {
                    "summary": "Роль не найдена",
                    "value": {
                        "code": "ROLE_NOT_FOUND",
                        "message": "Роль не найдена",
                        "details": {}
                    }
                }
            }
        }
    }
}

USER_NOT_FOUND = {
    "description": "Пользователь не найден",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": "USER_NOT_FOUND",
                "message": "Пользователь не найден",
                "details": {}
            }
        }
    }
}

USER_LOGIN_CONFLICT = {
    "description": "Пользователь с таким логином уже существует",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": "USER_USERNAME_EXISTS",
                "message": "Пользователь с таким логином уже существует",
                "details": {}
            }
        }
    }
}

USER_SESSION_404 = {
    "description": "Ресурс не найден",
    "content": {
        "application/json": {
            "examples": {
                "user_not_found": {
                    "summary": "Пользователь не найден",
                    "value": {
                        "code": "USER_NOT_FOUND",
                        "message": "Пользователь не найден",
                        "details": {}
                    }
                },
                "session_not_found": {
                    "summary": "Сессия не найдена или уже завершена",
                    "value": {
                        "code": "SESSION_NOT_FOUND",
                        "message": "Сессия не найдена или уже завершена",
                        "details": {}
                    }
                }
            }
        }
    }
}
