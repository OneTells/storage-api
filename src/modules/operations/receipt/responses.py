from core.schemes import ErrorResponse

RECEIPT_404 = {
    "description": "Сущность не найдена",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "supplier_not_found": {
                    "summary": "Поставщик не найден",
                    "value": {
                        "code": "SUPPLIER_NOT_FOUND",
                        "message": "Поставщик не найден",
                        "details": {},
                    },
                },
                "material_not_found": {
                    "summary": "Материал не найден",
                    "value": {
                        "code": "MATERIAL_NOT_FOUND",
                        "message": "Материал не найден",
                        "details": {},
                    },
                },
                "warehouse_not_found": {
                    "summary": "Склад не найден",
                    "value": {
                        "code": "WAREHOUSE_NOT_FOUND",
                        "message": "Склад не найден",
                        "details": {},
                    },
                },
                "batch_not_found": {
                    "summary": "Партия не найдена",
                    "value": {
                        "code": "BATCH_NOT_FOUND",
                        "message": "Партия не найден",
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
