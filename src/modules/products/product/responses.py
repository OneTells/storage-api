from core.schemes import ErrorResponse

MATERIAL_OR_RESOURCE_NOT_FOUND = {
    "description": "Материал или ресурс с указанным идентификатором не найден",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "material_not_found": {
                    "summary": "Материал не найден",
                    "value": {
                        "code": "MATERIAL_NOT_FOUND",
                        "message": "Материал не найден",
                        "details": {},
                    },
                },
                "resource_not_found": {
                    "summary": "Ресурс не найден",
                    "value": {
                        "code": "RESOURCE_NOT_FOUND",
                        "message": "Ресурс не найден",
                        "details": {},
                    },
                },
            },
        },
    },
}

PRODUCT_UPDATE_NOT_FOUND = {
    "description": "Продукт, материал или ресурс не найден",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "product_not_found": {
                    "summary": "Продукт не найден",
                    "value": {
                        "code": "PRODUCT_NOT_FOUND",
                        "message": "Продукт не найден",
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
                "resource_not_found": {
                    "summary": "Ресурс не найден",
                    "value": {
                        "code": "RESOURCE_NOT_FOUND",
                        "message": "Ресурс не найден",
                        "details": {},
                    },
                },
            },
        },
    },
}

PRODUCT_NOT_FOUND = {
    "description": "Продукт не найден",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": "PRODUCT_NOT_FOUND",
                "message": "Продукт не найден",
                "details": {}
            }
        }
    }
}

PRODUCT_MATERIAL_SHORTAGE_NOT_FOUND = {
    "description": "Продукт или склад не найден",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "product_not_found": {
                    "summary": "Продукт не найден",
                    "value": {
                        "code": "PRODUCT_NOT_FOUND",
                        "message": "Продукт не найден",
                        "details": {"product_ids": [1, 2]},
                    },
                },
                "warehouses_not_found": {
                    "summary": "Склад не найден",
                    "value": {
                        "code": "WAREHOUSES_NOT_FOUND",
                        "message": "Склад не найден",
                        "details": {"warehouse_ids": [99]},
                    },
                },
            },
        },
    },
}
