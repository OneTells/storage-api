"""Ошибки доменной логики применения складских операций к партиям."""


class StockOperationError(Exception):
    """Базовая ошибка складского эффекта (перехватывается в API и мапится в APIException)."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class InsufficientStockError(StockOperationError):
    def __init__(self, message: str = "Недостаточно остатка в партиях под операцию") -> None:
        super().__init__("INSUFFICIENT_STOCK", message)


class StockIntegrityError(StockOperationError):
    def __init__(self, message: str) -> None:
        super().__init__("STOCK_INTEGRITY", message)
