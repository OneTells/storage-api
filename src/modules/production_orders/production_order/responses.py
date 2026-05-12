from core.schemes import ErrorResponse

PRODUCTION_ORDER_404 = {
    "description": "Производственный заказ не найден",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "order_not_found": {
                    "summary": "Заказ не найден",
                    "value": {
                        "code": "PRODUCTION_ORDER_NOT_FOUND",
                        "message": "Производственный заказ не найден",
                        "details": {},
                    },
                },
            },
        },
    },
}

PRODUCTION_ORDER_MATERIAL_422 = {
    "description": "Ошибка изменения резерва",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "insufficient_reservation": {
                    "summary": "Недостаточно зарезервировано",
                    "value": {
                        "code": "INSUFFICIENT_MATERIAL_RESERVATION",
                        "message": "Недостаточно зарезервированного количества по материалу",
                        "details": {},
                    },
                },
            },
        },
    },
}
