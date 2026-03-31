from core.schemes import ErrorResponse

OPERATION_NOT_FOUND = {
    'description': 'Операция не найдена',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'example': {
                'detail': 'Операция не найдена',
            },
        },
    },
}
