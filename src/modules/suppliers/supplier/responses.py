from core.schemes import ErrorResponse

SUPPLIER_NOT_FOUND = {
    "description": "Поставщик не найден",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": "SUPPLIER_NOT_FOUND",
                "message": "Поставщик не найден",
                "details": {}
            }
        }
    }
}

SUPPLIER_NAME_CONFLICT = {
    "description": "Поставщик с таким названием уже существует",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": "SUPPLIER_NAME_EXISTS",
                "message": "Поставщик с таким названием уже существует",
                "details": {}
            }
        }
    }
}
