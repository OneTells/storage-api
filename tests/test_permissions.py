"""Раздел permissions — под router_with_auth (get_current_user)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests._helpers import API_V1


def test_get_permissions_read_response_list_unauthorized(client: TestClient) -> None:
    r = client.get(f"{API_V1}/permissions/", params={"page": 1})
    assert r.status_code == 401


def test_get_permissions_read_response_list_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.get(f"{API_V1}/permissions/", params={"page": 1}, headers=invalid_bearer)
    assert r.status_code == 403


def test_post_permission_create_response_unauthorized(client: TestClient) -> None:
    r = client.post(f"{API_V1}/permissions/", json={})
    assert r.status_code == 401


def test_post_permission_create_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.post(f"{API_V1}/permissions/", json={}, headers=invalid_bearer)
    assert r.status_code == 403


def test_get_permission_read_response_unauthorized(client: TestClient) -> None:
    r = client.get(f"{API_V1}/permissions/1")
    assert r.status_code == 401


def test_get_permission_read_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.get(f"{API_V1}/permissions/1", headers=invalid_bearer)
    assert r.status_code == 403


def test_put_permission_update_no_content_unauthorized(client: TestClient) -> None:
    r = client.put(f"{API_V1}/permissions/1", json={})
    assert r.status_code == 401


def test_put_permission_update_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.put(f"{API_V1}/permissions/1", json={}, headers=invalid_bearer)
    assert r.status_code == 403


def test_delete_permission_no_content_unauthorized(client: TestClient) -> None:
    r = client.delete(f"{API_V1}/permissions/1")
    assert r.status_code == 401


def test_delete_permission_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.delete(f"{API_V1}/permissions/1", headers=invalid_bearer)
    assert r.status_code == 403
