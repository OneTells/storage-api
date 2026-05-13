"""Раздел suppliers — под router_with_auth."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests._helpers import API_V1


def test_get_suppliers_read_response_list_unauthorized(client: TestClient) -> None:
    r = client.get(f"{API_V1}/suppliers/", params={"page": 1})
    assert r.status_code == 401


def test_get_suppliers_read_response_list_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.get(f"{API_V1}/suppliers/", params={"page": 1}, headers=invalid_bearer)
    assert r.status_code == 403


def test_post_supplier_create_response_unauthorized(client: TestClient) -> None:
    r = client.post(f"{API_V1}/suppliers/", json={})
    assert r.status_code == 401


def test_post_supplier_create_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.post(f"{API_V1}/suppliers/", json={}, headers=invalid_bearer)
    assert r.status_code == 403


def test_get_supplier_read_response_unauthorized(client: TestClient) -> None:
    r = client.get(f"{API_V1}/suppliers/1")
    assert r.status_code == 401


def test_get_supplier_read_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.get(f"{API_V1}/suppliers/1", headers=invalid_bearer)
    assert r.status_code == 403


def test_put_supplier_update_no_content_unauthorized(client: TestClient) -> None:
    r = client.put(f"{API_V1}/suppliers/1", json={})
    assert r.status_code == 401


def test_put_supplier_update_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.put(f"{API_V1}/suppliers/1", json={}, headers=invalid_bearer)
    assert r.status_code == 403
