from core.schemes import ErrorResponse

RETURN_TO_SUPPLIER_404 = {
    'description': 'Сущность не найдена',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'examples': {
                'supplier_not_found': {
                    'summary': 'Поставщик не найден',
                    'value': {'detail': 'Поставщик не найден'},
                },
                'object_unit_not_found': {
                    'summary': 'Единица объекта не найдена',
                    'value': {'detail': 'Единица объекта не найдена'},
                },
            },
        },
    },
}
