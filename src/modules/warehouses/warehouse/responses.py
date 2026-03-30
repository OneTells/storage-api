from core.schemes import ErrorCode, ErrorResponse

WAREHOUSE_NOT_FOUND = {
    'description': 'Склад не найден',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'example': {
                'code': ErrorCode.WAREHOUSE_NOT_FOUND,
                'message': 'Склад не найден',
                'params': {},
            },
        },
    },
}
