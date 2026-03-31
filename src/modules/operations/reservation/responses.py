from core.schemes import ErrorResponse

RESERVATION_404 = {
    'description': 'Сущность не найдена',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'examples': {
                'order_not_found': {
                    'summary': 'Заказ не найден',
                    'value': {'detail': 'Заказ не найден'},
                },
                'object_unit_not_found': {
                    'summary': 'Единица объекта не найдена',
                    'value': {'detail': 'Единица объекта не найдена'},
                },
            },
        },
    },
}
