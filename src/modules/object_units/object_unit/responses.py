from core.schemes import ErrorCode, ErrorResponse

OBJECT_UNIT_NOT_FOUND = {
    'description': 'Единица объекта не найдена',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'example': {
                'code': ErrorCode.OBJECT_UNIT_NOT_FOUND,
                'message': 'Единица объекта не найдена',
                'params': {},
            },
        },
    },
}
