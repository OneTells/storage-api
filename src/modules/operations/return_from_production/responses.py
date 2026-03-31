from core.schemes import ErrorResponse

RETURN_FROM_PRODUCTION_404 = {
    'description': 'Сущность не найдена',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'examples': {
                'production_order_not_found': {
                    'summary': 'Производственный заказ не найден',
                    'value': {'detail': 'Производственный заказ не найден'},
                },
                'object_unit_not_found': {
                    'summary': 'Единица объекта не найдена',
                    'value': {'detail': 'Единица объекта не найдена'},
                },
                'warehouse_not_found': {
                    'summary': 'Склад не найден',
                    'value': {'detail': 'Склад не найден'},
                },
            },
        },
    },
}
