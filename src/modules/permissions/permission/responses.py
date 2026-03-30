from core.schemes import ErrorResponse

PERMISSION_409 = {
    'description': 'Разрешение с таким именем или кодовым именем уже существует',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'examples': {
                'name_exists': {
                    'summary': 'Разрешение с таким именем уже существует',
                    'value': {
                        'detail': 'Разрешение с таким именем уже существует'
                    },
                },
                'codename_exists': {
                    'summary': 'Разрешение с таким кодовым именем уже существует',
                    'value': {
                        'detail': 'Разрешение с таким кодовым именем уже существует'
                    },
                },
            },
        },
    },
}

PERMISSION_NOT_FOUND = {
    'description': 'Разрешение не найдено',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'example': {
                'detail': 'Разрешение не найдено'
            },
        },
    },
}
