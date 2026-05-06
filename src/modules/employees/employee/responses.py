from core.schemes import ErrorResponse

EMPLOYEE_NOT_FOUND = {
    "description": "Сотрудник не найден",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": "EMPLOYEE_NOT_FOUND",
                "message": "Сотрудник не найден",
                "details": {}
            }
        }
    }
}
