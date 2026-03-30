from core.schemes import ErrorCode, ErrorResponse

USER_ROLE_404 = {
    'description': 'Пользователь или роль не найдены',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'examples': {
                'user_not_found': {
                    'summary': 'Пользователь не найден',
                    'value': {
                        'code': ErrorCode.USER_NOT_FOUND,
                        'message': 'Пользователь не найден',
                        'params': {},
                    },
                },
                'role_not_found': {
                    'summary': 'Роль не найдена',
                    'value': {
                        'code': ErrorCode.ROLE_NOT_FOUND,
                        'message': 'Роль не найдена',
                        'params': {},
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
                'code': ErrorCode.USER_NOT_FOUND,
                'message': 'Пользователь не найден',
                'params': {},
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
                'code': ErrorCode.USER_LOGIN_ALREADY_EXISTS,
                'message': 'Пользователь с таким логином уже существует',
                'params': {},
            },
        },
    },
}
