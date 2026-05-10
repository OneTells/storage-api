from core.schemes import ErrorResponse

PRODUCT_CATEGORY_NOT_FOUND = {
    "description": "Категория не найдена",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": "PRODUCT_CATEGORY_NOT_FOUND",
                "message": "Категория не найдена",
                "details": {},
            },
        },
    },
}

PRODUCT_CATEGORY_SUBCATEGORY_BAD_REQUEST = {
    "description": "Некорректная связь категорий",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "example": {
                "code": "PRODUCT_CATEGORY_SUBCATEGORY_SELF",
                "message": "Нельзя связать категорию саму с собой",
                "details": {},
            },
        },
    },
}

PRODUCT_CATEGORY_SUBCATEGORY_404 = {
    "description": "Категория или подкатегория не найдены, либо связь отсутствует",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "category_not_found": {
                    "summary": "Родительская категория не найдена",
                    "value": {
                        "code": "PRODUCT_CATEGORY_NOT_FOUND",
                        "message": "Категория не найдена",
                        "details": {},
                    },
                },
                "subcategory_not_found": {
                    "summary": "Подкатегория не найдена",
                    "value": {
                        "code": "PRODUCT_SUBCATEGORY_NOT_FOUND",
                        "message": "Подкатегория не найдена",
                        "details": {},
                    },
                },
                "link_not_found": {
                    "summary": "Связь не найдена",
                    "value": {
                        "code": "PRODUCT_CATEGORY_SUBCATEGORY_NOT_LINKED",
                        "message": "Подкатегория не привязана к этой категории",
                        "details": {},
                    },
                },
            },
        },
    },
}

PRODUCT_CATEGORY_PRODUCT_404 = {
    "description": "Категория или продукт не найдены, либо связь отсутствует",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "category_not_found": {
                    "summary": "Категория не найдена",
                    "value": {
                        "code": "PRODUCT_CATEGORY_NOT_FOUND",
                        "message": "Категория не найдена",
                        "details": {},
                    },
                },
                "product_not_found": {
                    "summary": "Продукт не найден",
                    "value": {
                        "code": "PRODUCT_NOT_FOUND",
                        "message": "Продукт не найден",
                        "details": {},
                    },
                },
                "link_not_found": {
                    "summary": "Связь не найдена",
                    "value": {
                        "code": "PRODUCT_CATEGORY_PRODUCT_NOT_LINKED",
                        "message": "Продукт не привязан к этой категории",
                        "details": {},
                    },
                },
            },
        },
    },
}

PRODUCT_CATEGORY_DELETE_CONFLICT = {
    "description": "Удаление категории невозможно из-за связанных записей",
    "model": ErrorResponse,
    "content": {
        "application/json": {
            "examples": {
                "all": {
                    "summary": "Дочерние категории и продукты",
                    "value": {
                        "code": "PRODUCT_CATEGORY_DELETE_CONFLICT",
                        "message": "Удаление категории невозможно из-за наличия дочерних категорий и продуктов",
                        "details": {},
                    },
                },
                "products": {
                    "summary": "Есть продукты в категории",
                    "value": {
                        "code": "PRODUCT_CATEGORY_DELETE_CONFLICT",
                        "message": "Удаление категории невозможно из-за наличия продуктов в категории",
                        "details": {},
                    },
                },
                "categories": {
                    "summary": "Есть дочерние категории",
                    "value": {
                        "code": "PRODUCT_CATEGORY_DELETE_CONFLICT",
                        "message": "Удаление категории невозможно из-за наличия дочерних категорий",
                        "details": {},
                    },
                },
            },
        },
    },
}
