from core.schemes import ErrorResponse

ROLE_PERMISSION_404 = {
    "description": "Роль или разрешение не найдены",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "role_not_found": {
                    "summary": "Роль не найдена",
                    "value": {
                        "code": "ROLE_NOT_FOUND",
                        "message": "Роль не найдена",
                        "details": {}
                    }
                },
                "permission_not_found": {
                    "summary": "Разрешение не найдено",
                    "value": {
                        "code": "PERMISSION_NOT_FOUND",
                        "message": "Разрешение не найдено",
                        "details": {}
                    }
                }
            }
        }
    }
}

ROLE_NOT_FOUND = {
    "description": "Роль не найдена",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": "ROLE_NOT_FOUND",
                "message": "Роль не найдена",
                "details": {}
            }
        }
    }
}

ROLE_NAME_CONFLICT = {
    "description": "Роль с таким именем уже существует",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": "ROLE_NAME_EXISTS",
                "message": "Роль с таким именем уже существует",
                "details": {}
            }
        }
    }
}
