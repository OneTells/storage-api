from core.schemes import ErrorResponse

OBJECT_UNIT_NOT_FOUND = {
    'description': 'Единица объекта не найдена',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'example': {
                'detail': 'Единица объекта не найдена'
            },
        },
    },
}
