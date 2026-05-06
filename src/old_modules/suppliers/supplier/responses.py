from core.schemes import ErrorResponse

SUPPLIER_NOT_FOUND = {
    'description': 'Поставщик не найден',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'example': {
                'detail': 'Поставщик не найден'
            },
        },
    },
}
