from core.schemes import ErrorResponse

CATEGORY_NOT_FOUND = {
    "description": "Категория не найдена",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {"detail": "Категория не найдена"},
        }
    },
}

CATEGORY_SUBCATEGORY_BAD_REQUEST = {
    "description": "Некорректная связь категорий",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": "CATEGORY_SUBCATEGORY_SELF",
                "message": "Нельзя связать категорию саму с собой",
                "details": {},
            },
        },
    },
}

CATEGORY_SUBCATEGORY_404 = {
    "description": "Категория или подкатегория не найдены, либо связь отсутствует",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "not_found": {
                    "summary": "Нет родительской или дочерней категории",
                    "value": {
                        "code": "SUBCATEGORY_NOT_FOUND",
                        "message": "Подкатегория или родительская категория не найдена",
                        "details": {},
                    },
                },
                "link_not_found": {
                    "summary": "Связь не найдена",
                    "value": {
                        "code": "CATEGORY_SUBCATEGORY_NOT_LINKED",
                        "message": "Подкатегория не привязана к этой категории",
                        "details": {},
                    },
                },
            },
        },
    },
}

CATEGORY_OBJECT_404 = {
    "description": "Категория или материал не найдены, либо связь отсутствует",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "category_or_material": {
                    "summary": "Нет категории или материала",
                    "value": {
                        "code": "CATEGORY_OBJECT_NOT_FOUND",
                        "message": "Категория или материал не найден",
                        "details": {},
                    },
                },
                "link_not_found": {
                    "summary": "Связь не найдена",
                    "value": {
                        "code": "CATEGORY_MATERIAL_NOT_LINKED",
                        "message": "Материал не привязан к этой категории",
                        "details": {},
                    },
                },
            },
        },
    },
}

CATEGORY_DELETE_CONFLICT = {
    "description": "Удаление категории невозможно из-за связанных записей",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "all": {
                    "summary": "Наличие дочерних категорий и материалов",
                    "value": {
                        "detail": "Удаление категории невозможно из-за наличия дочерних категорий и материалов"
                    },
                },
                "objects": {
                    "summary": "Наличие дочерних материалов",
                    "value": {
                        "detail": "Удаление категории невозможно из-за наличия дочерних материалов"
                    },
                },
                "categories": {
                    "summary": "Наличие дочерних категорий",
                    "value": {
                        "detail": "Удаление категории невозможно из-за наличия дочерних категорий"
                    },
                },
            },
        },
    },
}
