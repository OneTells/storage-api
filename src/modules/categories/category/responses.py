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

CATEGORY_OBJECT_404 = {
    "description": "Категория или объект не найдены",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "category_not_found": {
                    "summary": "Категория не найдена",
                    "value": {"detail": "Категория не найдена"},
                },
                "object_not_found": {
                    "summary": "Объект не найден",
                    "value": {"detail": "Объект не найден"},
                },
            },
        },
    },
}

CATEGORY_SUBCATEGORY_404 = {
    "description": "Категория или подкатегория не найдены",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "category_not_found": {
                    "summary": "Категория не найдена",
                    "value": {"detail": "Категория не найдена"},
                },
                "subcategory_not_found": {
                    "summary": "Подкатегория не найдена",
                    "value": {"detail": "Подкатегория не найдена"},
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
                    "summary": "Наличие дочерних категорий и объектов",
                    "value": {
                        "detail": "Удаление категории невозможно из-за наличия дочерних категорий и объектов"
                    }
                },
                "objects": {
                    "summary": "Наличие дочерних объектов",
                    "value": {
                        "detail": "Удаление категории невозможно из-за наличия дочерних объектов"
                    }
                },
                "categories": {
                    "summary": "Наличие дочерних категорий",
                    "value": {
                        "detail": "Удаление категории невозможно из-за наличия дочерних категорий"
                    }
                }
            }
        },
    },
}
