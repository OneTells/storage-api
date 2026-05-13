"""Раздел production_orders — под router_with_auth."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests._helpers import API_V1

_PO = f"{API_V1}/production-orders"


def test_get_production_orders_list_response_unauthorized(client: TestClient) -> None:
    r = client.get(f"{_PO}/")
    assert r.status_code == 401


def test_get_production_orders_list_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.get(f"{_PO}/", headers=invalid_bearer)
    assert r.status_code == 403


def test_post_production_order_create_response_unauthorized(client: TestClient) -> None:
    r = client.post(f"{_PO}/", json={})
    assert r.status_code == 401


def test_post_production_order_create_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.post(f"{_PO}/", json={}, headers=invalid_bearer)
    assert r.status_code == 403


def test_get_production_order_read_response_unauthorized(client: TestClient) -> None:
    r = client.get(f"{_PO}/1")
    assert r.status_code == 401


def test_get_production_order_read_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.get(f"{_PO}/1", headers=invalid_bearer)
    assert r.status_code == 403


def test_patch_production_order_read_response_unauthorized(client: TestClient) -> None:
    r = client.patch(f"{_PO}/1", json={})
    assert r.status_code == 401


def test_patch_production_order_read_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.patch(f"{_PO}/1", json={}, headers=invalid_bearer)
    assert r.status_code == 403


def test_post_production_order_material_reservation_add_no_content_unauthorized(client: TestClient) -> None:
    r = client.post(f"{_PO}/1/material-reservations/", json={})
    assert r.status_code == 401


def test_post_production_order_material_reservation_add_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.post(f"{_PO}/1/material-reservations/", json={}, headers=invalid_bearer)
    assert r.status_code == 403


def test_post_production_order_material_reservation_cancel_no_content_unauthorized(client: TestClient) -> None:
    r = client.post(f"{_PO}/1/material-reservations/cancel/", json={})
    assert r.status_code == 401


def test_post_production_order_material_reservation_cancel_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.post(f"{_PO}/1/material-reservations/cancel/", json={}, headers=invalid_bearer)
    assert r.status_code == 403
