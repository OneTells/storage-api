from core.schemes import ErrorResponse

SHIPMENT_404 = {
    'description': 'Сущность не найдена',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'examples': {
                'customer_not_found': {
                    'summary': 'Клиент не найден',
                    'value': {'detail': 'Клиент не найден'},
                },
                'object_unit_not_found': {
                    'summary': 'Единица объекта не найдена',
                    'value': {'detail': 'Единица объекта не найдена'},
                },
            },
        },
    },
}
