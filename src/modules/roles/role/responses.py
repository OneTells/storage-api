from core.schemes import ErrorCode, ErrorResponse

ROLE_PERMISSION_404 = {
    'description': 'Роль или разрешение не найдены',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'examples': {
                'role_not_found': {
                    'summary': 'Роль не найдена',
                    'value': {
                        'code': ErrorCode.ROLE_NOT_FOUND,
                        'message': 'Роль не найдена',
                        'params': {},
                    },
                },
                'permission_not_found': {
                    'summary': 'Разрешение не найдено',
                    'value': {
                        'code': ErrorCode.PERMISSION_NOT_FOUND,
                        'message': 'Разрешение не найдено',
                        'params': {},
                    },
                },
            },
        },
    },
}

ROLE_NOT_FOUND = {
    'description': 'Роль не найдена',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'example': {
                'code': ErrorCode.ROLE_NOT_FOUND,
                'message': 'Роль не найдена',
                'params': {},
            },
        },
    },
}

ROLE_NAME_CONFLICT = {
    'description': 'Роль с таким именем уже существует',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'example': {
                'code': ErrorCode.ROLE_ALREADY_EXISTS,
                'message': 'Роль с таким именем уже существует',
                'params': {},
            },
        },
    },
}
