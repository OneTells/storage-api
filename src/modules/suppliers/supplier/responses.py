from core.schemes import ErrorCode, ErrorResponse

SUPPLIER_NOT_FOUND = {
    'description': 'Поставщик не найден',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'example': {
                'code': ErrorCode.SUPPLIER_NOT_FOUND,
                'message': 'Поставщик не найден',
                'params': {},
            },
        },
    },
}
