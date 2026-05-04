from core.schemes import ErrorResponse

PASSWORD_LOGIN_INVALID_CREDENTIALS = {
    'description': 'Неверные учётные данные',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'example': {
                'code': 'INVALID_DATA',
                'message': 'Неверные учётные данные',
                'details': {}
            }
        }
    }
}
