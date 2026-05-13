"""Раздел products (каталог, категории, продукт) — под router_with_auth."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests._helpers import API_V1

_CATALOG = f"{API_V1}/products/catalog/"
_CATEGORIES = f"{API_V1}/products/categories"
_PRODUCTS = f"{API_V1}/products"


def test_get_products_catalog_read_response_unauthorized(client: TestClient) -> None:
    r = client.get(_CATALOG)
    assert r.status_code == 401


def test_get_products_catalog_read_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.get(_CATALOG, headers=invalid_bearer)
    assert r.status_code == 403


def test_post_product_category_create_response_unauthorized(client: TestClient) -> None:
    r = client.post(f"{_CATEGORIES}/", json={})
    assert r.status_code == 401


def test_post_product_category_create_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.post(f"{_CATEGORIES}/", json={}, headers=invalid_bearer)
    assert r.status_code == 403


def test_get_product_category_read_response_unauthorized(client: TestClient) -> None:
    r = client.get(f"{_CATEGORIES}/1")
    assert r.status_code == 401


def test_get_product_category_read_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.get(f"{_CATEGORIES}/1", headers=invalid_bearer)
    assert r.status_code == 403


def test_put_product_category_update_no_content_unauthorized(client: TestClient) -> None:
    r = client.put(f"{_CATEGORIES}/1", json={})
    assert r.status_code == 401


def test_put_product_category_update_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.put(f"{_CATEGORIES}/1", json={}, headers=invalid_bearer)
    assert r.status_code == 403


def test_delete_product_category_no_content_unauthorized(client: TestClient) -> None:
    r = client.delete(f"{_CATEGORIES}/1")
    assert r.status_code == 401


def test_delete_product_category_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.delete(f"{_CATEGORIES}/1", headers=invalid_bearer)
    assert r.status_code == 403


def test_post_product_category_bind_product_no_content_unauthorized(client: TestClient) -> None:
    r = client.post(f"{_CATEGORIES}/1/products/1")
    assert r.status_code == 401


def test_post_product_category_bind_product_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.post(f"{_CATEGORIES}/1/products/1", headers=invalid_bearer)
    assert r.status_code == 403


def test_delete_product_category_unbind_product_no_content_unauthorized(client: TestClient) -> None:
    r = client.delete(f"{_CATEGORIES}/1/products/1")
    assert r.status_code == 401


def test_delete_product_category_unbind_product_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.delete(f"{_CATEGORIES}/1/products/1", headers=invalid_bearer)
    assert r.status_code == 403


def test_post_product_category_bind_subcategory_no_content_unauthorized(client: TestClient) -> None:
    r = client.post(f"{_CATEGORIES}/1/subcategories/2")
    assert r.status_code == 401


def test_post_product_category_bind_subcategory_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.post(f"{_CATEGORIES}/1/subcategories/2", headers=invalid_bearer)
    assert r.status_code == 403


def test_delete_product_category_unbind_subcategory_no_content_unauthorized(client: TestClient) -> None:
    r = client.delete(f"{_CATEGORIES}/1/subcategories/2")
    assert r.status_code == 401


def test_delete_product_category_unbind_subcategory_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.delete(f"{_CATEGORIES}/1/subcategories/2", headers=invalid_bearer)
    assert r.status_code == 403


def test_post_product_create_response_unauthorized(client: TestClient) -> None:
    r = client.post(f"{_PRODUCTS}/", json={})
    assert r.status_code == 401


def test_post_product_create_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.post(f"{_PRODUCTS}/", json={}, headers=invalid_bearer)
    assert r.status_code == 403


def test_post_product_material_shortage_response_unauthorized(client: TestClient) -> None:
    r = client.post(f"{_PRODUCTS}/shortage", json={})
    assert r.status_code == 401


def test_post_product_material_shortage_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.post(f"{_PRODUCTS}/shortage", json={}, headers=invalid_bearer)
    assert r.status_code == 403


def test_get_product_read_response_unauthorized(client: TestClient) -> None:
    r = client.get(f"{_PRODUCTS}/1")
    assert r.status_code == 401


def test_get_product_read_response_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.get(f"{_PRODUCTS}/1", headers=invalid_bearer)
    assert r.status_code == 403


def test_put_product_update_no_content_unauthorized(client: TestClient) -> None:
    r = client.put(f"{_PRODUCTS}/1", json={})
    assert r.status_code == 401


def test_put_product_update_no_content_invalid_token(client: TestClient, invalid_bearer: dict[str, str]) -> None:
    r = client.put(f"{_PRODUCTS}/1", json={}, headers=invalid_bearer)
    assert r.status_code == 403
