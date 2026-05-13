"""Раздел customers — под router_with_auth."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests._helpers import API_V1


def test_get_customers_read_response_list_unauthorized(client: TestClient) -> None:
    r = client.get(f"{API_V1}/customers/", params={"page": 1})
    assert r.status_code == 401


def test_get_customers_read_response_list_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.get(f"{API_V1}/customers/", params={"page": 1}, headers=invalid_bearer)
    assert r.status_code == 403


def test_post_customer_create_response_unauthorized(client: TestClient) -> None:
    r = client.post(f"{API_V1}/customers/", json={})
    assert r.status_code == 401


def test_post_customer_create_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.post(f"{API_V1}/customers/", json={}, headers=invalid_bearer)
    assert r.status_code == 403


def test_get_customer_read_response_unauthorized(client: TestClient) -> None:
    r = client.get(f"{API_V1}/customers/1")
    assert r.status_code == 401


def test_get_customer_read_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.get(f"{API_V1}/customers/1", headers=invalid_bearer)
    assert r.status_code == 403


def test_put_customer_update_no_content_unauthorized(client: TestClient) -> None:
    r = client.put(f"{API_V1}/customers/1", json={})
    assert r.status_code == 401


def test_put_customer_update_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.put(f"{API_V1}/customers/1", json={}, headers=invalid_bearer)
    assert r.status_code == 403
