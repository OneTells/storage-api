from core.schemes import ErrorResponse

RESOURCE_NOT_FOUND = {
    "description": "Ресурс не найден",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": "RESOURCE_NOT_FOUND",
                "message": "Ресурс не найден",
                "details": {}
            }
        }
    }
}
