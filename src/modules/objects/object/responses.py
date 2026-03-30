from core.schemes import ErrorCode, ErrorResponse

OBJECT_NOT_FOUND = {
    'description': 'Объект не найден',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'example': {
                'code': ErrorCode.OBJECT_NOT_FOUND,
                'message': 'Объект не найден',
                'params': {},
            },
        },
    },
}

OBJECT_DELETE_CONFLICT = {
    'description': 'Объект не может быть удалён, так как есть связанные записи',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'example': {
                'code': ErrorCode.OBJECT_HAS_RELATIONS,
                'message': 'Объект не может быть удален, так как есть связанные записи',
                'params': {},
            },
        },
    },
}
