from core.schemes import ErrorResponse

OPERATION_HEADER_NOT_FOUND = {
    "description": "Операция указанного типа не найдена",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": "OPERATION_NOT_FOUND",
                "message": "Операция не найдена",
                "details": {},
            }
        }
    },
}
