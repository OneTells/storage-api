from core.schemes import ErrorResponse

RECEIPT_404 = {
    'description': 'Сущность не найдена',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'examples': {
                'supplier_not_found': {
                    'summary': 'Поставщик не найден',
                    'value': {'detail': 'Поставщик не найден'},
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
