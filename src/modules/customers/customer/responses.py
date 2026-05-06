from core.schemes import ErrorResponse

CUSTOMER_NOT_FOUND = {
    "description": "Клиент не найден",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": "CUSTOMER_NOT_FOUND",
                "message": "Клиент не найден",
                "details": {}
            }
        }
    }
}

CUSTOMER_NAME_CONFLICT = {
    "description": "Клиент с таким названием уже существует",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": "CUSTOMER_NAME_EXISTS",
                "message": "Клиент с таким названием уже существует",
                "details": {}
            }
        }
    }
}
