from core.schemes import ErrorCode, ErrorResponse

RECEIPT_404 = {
    'description': 'Сущность не найдена',
    'model': ErrorResponse,
    'content': {
        'application/json': {
            'examples': {
                'supplier_not_found': {
                    'summary': 'Поставщик не найден',
                    'value': {
                        'code': ErrorCode.SUPPLIER_NOT_FOUND,
                        'message': 'Поставщик не найден',
                        'params': {},
                    },
                },
                'object_not_found': {
                    'summary': 'Объект не найден',
                    'value': {
                        'code': ErrorCode.OBJECT_NOT_FOUND,
                        'message': 'Объект не найден',
                        'params': {},
                    },
                },
                'warehouse_not_found': {
                    'summary': 'Склад не найден',
                    'value': {
                        'code': ErrorCode.WAREHOUSE_NOT_FOUND,
                        'message': 'Склад не найден',
                        'params': {},
                    },
                },
            },
        },
    },
}
