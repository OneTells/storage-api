"""Раздел units — под router_with_auth."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests._helpers import API_V1


def test_get_units_read_response_list_unauthorized(client: TestClient) -> None:
    r = client.get(f"{API_V1}/units/")
    assert r.status_code == 401


def test_get_units_read_response_list_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.get(f"{API_V1}/units/", headers=invalid_bearer)
    assert r.status_code == 403


def test_get_units_read_response_list_page_query_optional_invariant(client: TestClient) -> None:
    """Доп. инвариант: с page=1 поведение авторизации то же (без БД)."""
    r = client.get(f"{API_V1}/units/", params={"page": 1})
    assert r.status_code == 401
