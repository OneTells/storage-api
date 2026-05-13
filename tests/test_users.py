"""Раздел users (список, профиль, карточка пользователя) — под router_with_auth."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests._helpers import API_V1

_USERS = f"{API_V1}/users"


def test_get_users_read_response_list_unauthorized(client: TestClient) -> None:
    r = client.get(f"{_USERS}/", params={"page": 1})
    assert r.status_code == 401


def test_get_users_read_response_list_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.get(f"{_USERS}/", params={"page": 1}, headers=invalid_bearer)
    assert r.status_code == 403


def test_get_profile_read_response_unauthorized(client: TestClient) -> None:
    r = client.get(f"{_USERS}/profile")
    assert r.status_code == 401


def test_get_profile_read_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.get(f"{_USERS}/profile", headers=invalid_bearer)
    assert r.status_code == 403


def test_put_profile_update_no_content_unauthorized(client: TestClient) -> None:
    r = client.put(f"{_USERS}/profile", json={})
    assert r.status_code == 401


def test_put_profile_update_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.put(f"{_USERS}/profile", json={}, headers=invalid_bearer)
    assert r.status_code == 403


def test_put_profile_password_change_no_content_unauthorized(client: TestClient) -> None:
    r = client.put(f"{_USERS}/profile/password", json={})
    assert r.status_code == 401


def test_put_profile_password_change_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.put(f"{_USERS}/profile/password", json={}, headers=invalid_bearer)
    assert r.status_code == 403


def test_delete_profile_session_terminate_no_content_unauthorized(client: TestClient) -> None:
    r = client.delete(f"{_USERS}/profile/sessions/x")
    assert r.status_code == 401


def test_delete_profile_session_terminate_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.delete(f"{_USERS}/profile/sessions/x", headers=invalid_bearer)
    assert r.status_code == 403


def test_post_user_create_response_unauthorized(client: TestClient) -> None:
    r = client.post(f"{_USERS}/", json={})
    assert r.status_code == 401


def test_post_user_create_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.post(f"{_USERS}/", json={}, headers=invalid_bearer)
    assert r.status_code == 403


def test_get_user_read_with_permissions_response_unauthorized(client: TestClient) -> None:
    r = client.get(f"{_USERS}/1")
    assert r.status_code == 401


def test_get_user_read_with_permissions_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.get(f"{_USERS}/1", headers=invalid_bearer)
    assert r.status_code == 403


def test_put_user_update_no_content_unauthorized(client: TestClient) -> None:
    r = client.put(f"{_USERS}/1", json={})
    assert r.status_code == 401


def test_put_user_update_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.put(f"{_USERS}/1", json={}, headers=invalid_bearer)
    assert r.status_code == 403


def test_delete_user_no_content_unauthorized(client: TestClient) -> None:
    r = client.delete(f"{_USERS}/1")
    assert r.status_code == 401


def test_delete_user_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.delete(f"{_USERS}/1", headers=invalid_bearer)
    assert r.status_code == 403


def test_post_user_role_assign_no_content_unauthorized(client: TestClient) -> None:
    r = client.post(f"{_USERS}/1/roles", json={})
    assert r.status_code == 401


def test_post_user_role_assign_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.post(f"{_USERS}/1/roles", json={}, headers=invalid_bearer)
    assert r.status_code == 403


def test_delete_user_role_remove_no_content_unauthorized(client: TestClient) -> None:
    r = client.delete(f"{_USERS}/1/roles/1")
    assert r.status_code == 401


def test_delete_user_role_remove_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.delete(f"{_USERS}/1/roles/1", headers=invalid_bearer)
    assert r.status_code == 403


def test_put_user_password_change_no_content_unauthorized(client: TestClient) -> None:
    r = client.put(f"{_USERS}/1/password", json={})
    assert r.status_code == 401


def test_put_user_password_change_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.put(f"{_USERS}/1/password", json={}, headers=invalid_bearer)
    assert r.status_code == 403


def test_get_user_sessions_read_response_unauthorized(client: TestClient) -> None:
    r = client.get(f"{_USERS}/1/sessions")
    assert r.status_code == 401


def test_get_user_sessions_read_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.get(f"{_USERS}/1/sessions", headers=invalid_bearer)
    assert r.status_code == 403


def test_delete_user_session_terminate_no_content_unauthorized(client: TestClient) -> None:
    r = client.delete(f"{_USERS}/1/sessions/x")
    assert r.status_code == 401


def test_delete_user_session_terminate_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.delete(f"{_USERS}/1/sessions/x", headers=invalid_bearer)
    assert r.status_code == 403
