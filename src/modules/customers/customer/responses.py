from core.schemes import ErrorCode, ErrorResponse

CUSTOMER_NOT_FOUND = {
    'description': 'Клиент не найден',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'example': {
                'code': ErrorCode.CUSTOMER_NOT_FOUND,
                'message': 'Клиент не найден',
                'params': {},
            },
        },
    },
}
