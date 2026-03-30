from core.schemes import ErrorCode, ErrorResponse

CATEGORY_NOT_FOUND = {
    'description': 'Категория не найдена',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'example': {
                'code': ErrorCode.CATEGORY_NOT_FOUND,
                'message': 'Категория не найдена',
                'params': {},
            },
        },
    },
}
