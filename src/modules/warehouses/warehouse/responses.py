from core.schemes import ErrorResponse

WAREHOUSE_NOT_FOUND = {
    "description": "Склад не найден",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": "WAREHOUSE_NOT_FOUND",
                "message": "Склад не найден",
                "details": {}
            }
        }
    }
}

WAREHOUSE_NAME_CONFLICT = {
    "description": "Склад с таким названием уже существует",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": "WAREHOUSE_NAME_EXISTS",
                "message": "Склад с таким названием уже существует",
                "details": {}
            }
        }
    }
}
