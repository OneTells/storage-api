from core.schemes import ErrorResponse

RESERVATION_404 = {
    "description": "Сущность не найдена",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "batch_not_found": {
                    "summary": "Партия не найдена",
                    "value": {
                        "code": "BATCH_NOT_FOUND",
                        "message": "Партия не найдена",
                        "details": {},
                    },
                },
                "not_enough_quantity": {
                    "summary": "Недостаточно доступного объёма в партии",
                    "value": {
                        "code": "INSUFFICIENT_BATCH_QUANTITY",
                        "message": "Недостаточно остатка в партии",
                        "details": {},
                    },
                },
                "reservation_not_found": {
                    "summary": "Резервирование не найдено",
                    "value": {
                        "code": "RESERVATION_NOT_FOUND",
                        "message": "Резервирование не найдено",
                        "details": {},
                    },
                },
                "operation_not_found": {
                    "summary": "Операция не найдена",
                    "value": {
                        "code": "OPERATION_NOT_FOUND",
                        "message": "Операция не найдена",
                        "details": {},
                    },
                },
            },
        },
    },
}
