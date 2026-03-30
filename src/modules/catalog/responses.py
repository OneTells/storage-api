from core.schemes import ErrorResponse

CATEGORY_NOT_FOUND = {
    'description': 'Категория не найдена',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'example': {
                'detail': 'Категория не найдена'
            },
        },
    },
}
