from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Depends, Query

from core.methods import get_connection, require_permissions
from modules.products.catalog import repositories
from modules.products.catalog.schemes import CatalogReadResponse

router = APIRouter(prefix="/catalog")


@router.get(
    "/",
    response_model=CatalogReadResponse,
    dependencies=[Depends(require_permissions("products.catalog.read"))],
    summary="Каталог: категории, позиции и связи",
)
async def get_products_catalog(
    connection: Annotated[Connection, Depends(get_connection)],
    is_active_products: Annotated[bool | None, Query(description="Фильтр по активности продукта")] = None,
):
    categories = await repositories.fetch_catalog_categories(connection)
    products = await repositories.fetch_catalog_products(connection, is_active_products)

    link_rows = await repositories.fetch_catalog_category_product_links(connection, [row["id"] for row in products])
    subcategory_link_rows = await repositories.fetch_catalog_category_subcategory_links(connection)

    return CatalogReadResponse.model_validate(
        {
            "categories": [dict(x) for x in categories],
            "products": [
                {
                    **x,
                    "output_material": {
                        "id": x["output_material_id"],
                        "name": x["output_material_name"],
                        "quantity": x["quantity"],
                        "unit": {
                            "id": x["output_material_unit_id"],
                            "name": x["output_material_unit_name"],
                            "short_name": x["output_material_unit_short_name"],
                        },
                    },
                }
                for x in products
            ],
            "category_product_relations": [dict(x) for x in link_rows],
            "category_subcategory_relations": [dict(x) for x in subcategory_link_rows],
        }
    )
