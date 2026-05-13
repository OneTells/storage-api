"""Корневой маршрут приложения (вне /api/v1)."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_root_redirect_response_without_follow(client: TestClient) -> None:
    """Редирект на base_url: статус 3xx (без обращения к БД)."""
    r = client.get("/", follow_redirects=False)
    assert r.status_code in (301, 302, 303, 307, 308)


def test_root_redirect_not_server_error(client: TestClient) -> None:
    r = client.get("/", follow_redirects=False)
    assert r.status_code < 500
