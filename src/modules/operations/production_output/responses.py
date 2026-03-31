from core.schemes import ErrorResponse

PRODUCTION_OUTPUT_404 = {
    'description': 'Сущность не найдена',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'examples': {
                'production_order_not_found': {
                    'summary': 'Производственный заказ не найден',
                    'value': {'detail': 'Производственный заказ не найден'},
                },
                'object_not_found': {
                    'summary': 'Объект не найден',
                    'value': {'detail': 'Объект не найден'},
                },
                'warehouse_not_found': {
                    'summary': 'Склад не найден',
                    'value': {'detail': 'Склад не найден'},
                },
            },
        },
    },
}
