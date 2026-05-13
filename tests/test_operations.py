"""Раздел operations — под router_with_auth; по одной паре тестов на каждую ручку (имена из типа операции)."""

from __future__ import annotations

import sys
from collections.abc import Callable
from typing import Any

from fastapi.testclient import TestClient

from tests._helpers import API_V1

_OPERATION_SEGMENTS = (
    "receipts",
    "shipments",
    "production_outputs",
    "write_offs_to_production",
    "write_offs",
    "inventory_adjustments",
    "transfers",
    "reservations",
)


def _register_operation_route_tests() -> None:
    g = sys.modules[__name__].__dict__
    specs: list[tuple[str, str, str, dict[str, Any]]] = []
    for seg in _OPERATION_SEGMENTS:
        base = f"{API_V1}/operations/{seg}"
        specs.append((f"get_{seg}_list_response", "GET", base, {"params": {"page": 1}}))
        specs.append((f"get_{seg}_read_response", "GET", f"{base}/1", {}))
        specs.append((f"post_{seg}_create_response", "POST", base, {}))
        specs.append((f"patch_{seg}_update_no_content", "PATCH", f"{base}/1", {"json": {}}))

    for logical_name, method, url, extra in specs:

        def _unauthorized(
            client: TestClient,
            *,
            _m: str = method,
            _u: str = url,
            _e: dict[str, Any] = extra,
        ) -> None:
            assert client.request(_m, _u, **_e).status_code == 401

        def _invalid_token(
            client: TestClient,
            invalid_bearer: dict[str, str],
            *,
            _m: str = method,
            _u: str = url,
            _e: dict[str, Any] = extra,
        ) -> None:
            assert client.request(_m, _u, headers=invalid_bearer, **_e).status_code == 403

        ua: Callable[..., None] = _unauthorized
        ib: Callable[..., None] = _invalid_token
        ua.__name__ = f"test_{logical_name}_unauthorized_without_bearer"
        ib.__name__ = f"test_{logical_name}_forbidden_with_invalid_bearer"
        ua.__module__ = __name__
        ib.__module__ = __name__
        g[ua.__name__] = ua
        g[ib.__name__] = ib


_register_operation_route_tests()
