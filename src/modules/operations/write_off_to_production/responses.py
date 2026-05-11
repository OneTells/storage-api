from core.schemes import ErrorResponse

WRITE_OFF_TO_PRODUCTION_404 = {
    "description": "Сущность не найдена",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "production_order_not_found": {
                    "summary": "Производственный заказ не найден",
                    "value": {
                        "code": "PRODUCTION_ORDER_NOT_FOUND",
                        "message": "Производственный заказ не найден",
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
                "material_not_found": {
                    "summary": "Материал не найден",
                    "value": {
                        "code": "MATERIAL_NOT_FOUND",
                        "message": "Материал не найден",
                        "details": {},
                    },
                },
                "batch_not_found": {
                    "summary": "Партия не найдена",
                    "value": {
                        "code": "BATCH_NOT_FOUND",
                        "message": "Партия не найдена",
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
