from core.schemes import ErrorResponse

MATERIAL_NOT_FOUND = {
    "description": "Материал не найден",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": "MATERIAL_NOT_FOUND",
                "message": "Материал не найден",
                "details": {},
            },
        },
    },
}

UNIT_NOT_FOUND = {
    "description": "Единица измерения не найдена",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": "UNIT_NOT_FOUND",
                "message": "Единица измерения не найдена",
                "details": {},
            },
        },
    },
}

MATERIAL_SKU_CONFLICT = {
    "description": "Материал с таким артикулом уже существует",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": "MATERIAL_SKU_EXISTS",
                "message": "Материал с таким артикулом уже существует",
                "details": {},
            },
        },
    },
}
