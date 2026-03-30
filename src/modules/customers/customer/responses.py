from core.schemes import ErrorResponse

CUSTOMER_NOT_FOUND = {
    'description': 'Клиент не найден',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'example': {
                'detail': 'Клиент не найден'
            },
        },
    },
}
