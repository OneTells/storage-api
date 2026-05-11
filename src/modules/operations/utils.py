"""Аналитические функции складских операций (без БД)."""

from __future__ import annotations

from decimal import Decimal


def inventory_line_qty_delta(*, expected_qty: Decimal, actual_qty: Decimal) -> Decimal:
    """Разница факт − план по строке инвентаризации (излишек положительный, недостача отрицательная)."""

    return actual_qty - expected_qty
