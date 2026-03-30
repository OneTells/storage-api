from core.schemes import ErrorResponse

WAREHOUSE_NOT_FOUND = {
    'description': 'Склад не найден',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'example': {
                'detail': 'Склад не найден'
            },
        },
    },
}
