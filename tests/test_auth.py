"""Модуль auth: без общего Depends(get_current_user) на роутере, кроме logout."""

from __future__ import annotations

from tests._helpers import API_V1


def test_password_login_token_response_validation_empty_body_unprocessable(client) -> None:
    """TokenResponse не отдаётся при пустом теле — UNPROCESSABLE_ENTITY (422)."""
    r = client.post(f"{API_V1}/auth/password", json={})
    assert r.status_code == 422


def test_password_login_token_response_validation_password_too_short_unprocessable(client) -> None:
    r = client.post(
        f"{API_V1}/auth/password",
        json={"username": "abc", "password": "short"},
    )
    assert r.status_code == 422


def test_password_login_token_response_validation_username_too_short_unprocessable(client) -> None:
    r = client.post(
        f"{API_V1}/auth/password",
        json={"username": "ab", "password": "12345678"},
    )
    assert r.status_code == 422


def test_logout_no_content_requires_authentication(client) -> None:
    """logout: 204 при успехе; без сессии — 401 (см. UNAUTHORIZED_RESPONSE в api.py)."""
    r = client.post(f"{API_V1}/auth/logout")
    assert r.status_code == 401


def test_logout_no_content_rejects_invalid_bearer(client, invalid_bearer: dict[str, str]) -> None:
    r = client.post(f"{API_V1}/auth/logout", headers=invalid_bearer)
    assert r.status_code == 403
