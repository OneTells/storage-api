from core.schemes import ErrorResponse

ROLE_PERMISSION_404 = {
    'description': 'Роль или разрешение не найдены',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'examples': {
                'role_not_found': {
                    'summary': 'Роль не найдена',
                    'value': {
                        'detail': 'Роль не найдена'
                    },
                },
                'permission_not_found': {
                    'summary': 'Разрешение не найдено',
                    'value': {
                        'detail': 'Разрешение не найдено'
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
                'detail': 'Роль не найдена'
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
                'detail': 'Роль с таким именем уже существует'
            },
        },
    },
}
