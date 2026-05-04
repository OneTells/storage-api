from core.schemes import ErrorResponse

PERMISSION_409 = {
    "description": "Разрешение с таким именем или кодовым именем уже существует",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "name_exists": {
                    "summary": "Разрешение с таким именем уже существует",
                    "value": {
                        "code": "PERMISSION_NAME_EXISTS",
                        "message": "Разрешение с таким именем уже существует",
                        "details": {}
                    }
                },
                "codename_exists": {
                    "summary": "Разрешение с таким кодовым именем уже существует",
                    "value": {
                        "code": "PERMISSION_CODENAME_EXISTS",
                        "message": "Разрешение с таким кодовым именем уже существует",
                        "details": {}
                    }
                }
            }
        }
    }
}

PERMISSION_NOT_FOUND = {
    "description": "Разрешение не найдено",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": "PERMISSION_NOT_FOUND",
                "message": "Разрешение не найдено",
                "details": {}
            }
        }
    }
}
