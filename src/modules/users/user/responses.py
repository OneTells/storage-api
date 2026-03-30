from core.schemes import ErrorResponse

USER_ROLE_404 = {
    'description': 'Пользователь или роль не найдены',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'examples': {
                'user_not_found': {
                    'summary': 'Пользователь не найден',
                    'value': {
                        'detail': 'Пользователь не найден'
                    },
                },
                'role_not_found': {
                    'summary': 'Роль не найдена',
                    'value': {
                        'detail': 'Роль не найдена'
                    },
                },
            },
        },
    },
}

USER_NOT_FOUND = {
    'description': 'Пользователь не найден',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'example': {
                'detail': 'Пользователь не найден'
            },
        },
    },
}

USER_LOGIN_CONFLICT = {
    'description': 'Пользователь с таким логином уже существует',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'example': {
                'detail': 'Пользователь с таким логином уже существует'
            },
        },
    },
}
