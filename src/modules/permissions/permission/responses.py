from core.schemes import ErrorCode, ErrorResponse

PERMISSION_409 = {
    'description': 'Разрешение с таким именем или кодовым именем уже существует',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'examples': {
                'name_exists': {
                    'summary': 'Разрешение с таким именем уже существует',
                    'value': {
                        'code': ErrorCode.PERMISSION_NAME_ALREADY_EXISTS,
                        'message': 'Разрешение с таким именем уже существует',
                        'params': {},
                    },
                },
                'codename_exists': {
                    'summary': 'Разрешение с таким кодовым именем уже существует',
                    'value': {
                        'code': ErrorCode.PERMISSION_CODENAME_ALREADY_EXISTS,
                        'message': 'Разрешение с таким кодовым именем уже существует',
                        'params': {},
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
                'code': ErrorCode.PERMISSION_NOT_FOUND,
                'message': 'Разрешение не найдено',
                'params': {},
            },
        },
    },
}
