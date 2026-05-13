"""Раздел materials (каталог, категории, материал) — под router_with_auth."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests._helpers import API_V1

_CATALOG = f"{API_V1}/materials/catalog/"
_CATEGORIES = f"{API_V1}/materials/categories"
_MATERIALS = f"{API_V1}/materials"


def test_get_materials_catalog_read_response_unauthorized(client: TestClient) -> None:
    r = client.get(_CATALOG)
    assert r.status_code == 401


def test_get_materials_catalog_read_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.get(_CATALOG, headers=invalid_bearer)
    assert r.status_code == 403


def test_post_material_category_create_response_unauthorized(client: TestClient) -> None:
    r = client.post(f"{_CATEGORIES}/", json={})
    assert r.status_code == 401


def test_post_material_category_create_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.post(f"{_CATEGORIES}/", json={}, headers=invalid_bearer)
    assert r.status_code == 403


def test_get_material_category_read_response_unauthorized(client: TestClient) -> None:
    r = client.get(f"{_CATEGORIES}/1")
    assert r.status_code == 401


def test_get_material_category_read_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.get(f"{_CATEGORIES}/1", headers=invalid_bearer)
    assert r.status_code == 403


def test_put_material_category_update_no_content_unauthorized(client: TestClient) -> None:
    r = client.put(f"{_CATEGORIES}/1", json={})
    assert r.status_code == 401


def test_put_material_category_update_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.put(f"{_CATEGORIES}/1", json={}, headers=invalid_bearer)
    assert r.status_code == 403


def test_delete_material_category_no_content_unauthorized(client: TestClient) -> None:
    r = client.delete(f"{_CATEGORIES}/1")
    assert r.status_code == 401


def test_delete_material_category_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.delete(f"{_CATEGORIES}/1", headers=invalid_bearer)
    assert r.status_code == 403


def test_post_material_category_bind_material_no_content_unauthorized(client: TestClient) -> None:
    r = client.post(f"{_CATEGORIES}/1/materials/1")
    assert r.status_code == 401


def test_post_material_category_bind_material_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.post(f"{_CATEGORIES}/1/materials/1", headers=invalid_bearer)
    assert r.status_code == 403


def test_delete_material_category_unbind_material_no_content_unauthorized(client: TestClient) -> None:
    r = client.delete(f"{_CATEGORIES}/1/materials/1")
    assert r.status_code == 401


def test_delete_material_category_unbind_material_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.delete(f"{_CATEGORIES}/1/materials/1", headers=invalid_bearer)
    assert r.status_code == 403


def test_post_material_category_bind_subcategory_no_content_unauthorized(client: TestClient) -> None:
    r = client.post(f"{_CATEGORIES}/1/subcategories/2")
    assert r.status_code == 401


def test_post_material_category_bind_subcategory_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.post(f"{_CATEGORIES}/1/subcategories/2", headers=invalid_bearer)
    assert r.status_code == 403


def test_delete_material_category_unbind_subcategory_no_content_unauthorized(client: TestClient) -> None:
    r = client.delete(f"{_CATEGORIES}/1/subcategories/2")
    assert r.status_code == 401


def test_delete_material_category_unbind_subcategory_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.delete(f"{_CATEGORIES}/1/subcategories/2", headers=invalid_bearer)
    assert r.status_code == 403


def test_post_material_create_response_unauthorized(client: TestClient) -> None:
    r = client.post(f"{_MATERIALS}/", json={})
    assert r.status_code == 401


def test_post_material_create_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.post(f"{_MATERIALS}/", json={}, headers=invalid_bearer)
    assert r.status_code == 403


def test_get_material_read_response_unauthorized(client: TestClient) -> None:
    r = client.get(f"{_MATERIALS}/1")
    assert r.status_code == 401


def test_get_material_read_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.get(f"{_MATERIALS}/1", headers=invalid_bearer)
    assert r.status_code == 403


def test_put_material_update_no_content_unauthorized(client: TestClient) -> None:
    r = client.put(f"{_MATERIALS}/1", json={})
    assert r.status_code == 401


def test_put_material_update_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.put(f"{_MATERIALS}/1", json={}, headers=invalid_bearer)
    assert r.status_code == 403
