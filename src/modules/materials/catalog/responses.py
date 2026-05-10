from core.schemes import ErrorResponse

MATERIALS_CATALOG_READ_NOT_FOUND = {
    "description": "Склад не найден",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "warehouse_not_found": {
                    "summary": "Нет склада",
                    "value": {"code": "WAREHOUSE_NOT_FOUND", "message": "Склад не найден", "details": {}},
                },
            },
        },
    },
}
