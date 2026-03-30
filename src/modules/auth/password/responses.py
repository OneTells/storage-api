from core.schemes import ErrorResponse

PASSWORD_LOGIN_INVALID_CREDENTIALS = {
    'description': 'Неверные учётные данные',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'example': {
                'detail': 'Неверные учётные данные'
            },
        },
    },
}
