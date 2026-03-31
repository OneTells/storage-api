from core.schemes import ErrorResponse

INVENTORY_ADJUSTMENT_404 = {
    'description': 'Сущность не найдена',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'examples': {
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
