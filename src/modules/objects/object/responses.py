from core.schemes import ErrorResponse

OBJECT_NOT_FOUND = {
    'description': 'Объект не найден',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'example': {
                'detail': 'Объект не найден'
            },
        },
    },
}

OBJECT_DELETE_CONFLICT = {
    'description': 'Объект не может быть удалён из-за связанных записей',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'example': {
                'detail': 'Объект не может быть удален, так как есть связанные записи'
            },
        },
    },
}
