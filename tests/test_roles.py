"""Раздел roles — под router_with_auth."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests._helpers import API_V1


def test_get_roles_read_response_list_unauthorized(client: TestClient) -> None:
    r = client.get(f"{API_V1}/roles/", params={"page": 1})
    assert r.status_code == 401


def test_get_roles_read_response_list_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.get(f"{API_V1}/roles/", params={"page": 1}, headers=invalid_bearer)
    assert r.status_code == 403


def test_post_role_create_response_unauthorized(client: TestClient) -> None:
    r = client.post(f"{API_V1}/roles/", json={})
    assert r.status_code == 401


def test_post_role_create_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.post(f"{API_V1}/roles/", json={}, headers=invalid_bearer)
    assert r.status_code == 403


def test_get_role_read_response_unauthorized(client: TestClient) -> None:
    r = client.get(f"{API_V1}/roles/1")
    assert r.status_code == 401


def test_get_role_read_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.get(f"{API_V1}/roles/1", headers=invalid_bearer)
    assert r.status_code == 403


def test_put_role_update_no_content_unauthorized(client: TestClient) -> None:
    r = client.put(f"{API_V1}/roles/1", json={})
    assert r.status_code == 401


def test_put_role_update_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.put(f"{API_V1}/roles/1", json={}, headers=invalid_bearer)
    assert r.status_code == 403


def test_delete_role_no_content_unauthorized(client: TestClient) -> None:
    r = client.delete(f"{API_V1}/roles/1")
    assert r.status_code == 401


def test_delete_role_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.delete(f"{API_V1}/roles/1", headers=invalid_bearer)
    assert r.status_code == 403


def test_post_role_permission_assign_no_content_unauthorized(client: TestClient) -> None:
    r = client.post(f"{API_V1}/roles/1/permissions", json={})
    assert r.status_code == 401


def test_post_role_permission_assign_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.post(f"{API_V1}/roles/1/permissions", json={}, headers=invalid_bearer)
    assert r.status_code == 403


def test_delete_role_permission_remove_no_content_unauthorized(client: TestClient) -> None:
    r = client.delete(f"{API_V1}/roles/1/permissions/1")
    assert r.status_code == 401


def test_delete_role_permission_remove_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.delete(f"{API_V1}/roles/1/permissions/1", headers=invalid_bearer)
    assert r.status_code == 403
