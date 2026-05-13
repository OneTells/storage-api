"""Раздел warehouses — под router_with_auth."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests._helpers import API_V1


def test_get_warehouses_read_response_list_unauthorized(client: TestClient) -> None:
    r = client.get(f"{API_V1}/warehouses/", params={"page": 1})
    assert r.status_code == 401


def test_get_warehouses_read_response_list_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.get(f"{API_V1}/warehouses/", params={"page": 1}, headers=invalid_bearer)
    assert r.status_code == 403


def test_post_warehouse_create_response_unauthorized(client: TestClient) -> None:
    r = client.post(f"{API_V1}/warehouses/", json={})
    assert r.status_code == 401


def test_post_warehouse_create_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.post(f"{API_V1}/warehouses/", json={}, headers=invalid_bearer)
    assert r.status_code == 403


def test_get_warehouse_read_response_unauthorized(client: TestClient) -> None:
    r = client.get(f"{API_V1}/warehouses/1")
    assert r.status_code == 401


def test_get_warehouse_read_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.get(f"{API_V1}/warehouses/1", headers=invalid_bearer)
    assert r.status_code == 403


def test_put_warehouse_update_no_content_unauthorized(client: TestClient) -> None:
    r = client.put(f"{API_V1}/warehouses/1", json={})
    assert r.status_code == 401


def test_put_warehouse_update_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.put(f"{API_V1}/warehouses/1", json={}, headers=invalid_bearer)
    assert r.status_code == 403
