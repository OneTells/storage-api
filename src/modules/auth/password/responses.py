from core.schemes import ErrorCode, ErrorResponse

PASSWORD_LOGIN_INVALID_CREDENTIALS = {
    'description': 'Неверные учётные данные',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'example': {
                'code': ErrorCode.INVALID_CREDENTIALS,
                'message': 'Неверные учётные данные',
                'params': {},
            },
        },
    },
}
