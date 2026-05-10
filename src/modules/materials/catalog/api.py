from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Depends, Query

from core.exceptions import APIException
from core.methods import get_connection, require_permissions
from modules.materials.catalog import repositories
from modules.materials.catalog.responses import MATERIALS_CATALOG_READ_NOT_FOUND
from modules.materials.catalog.schemes import CatalogReadResponse

router = APIRouter(prefix="/catalog")


@router.get(
    "/",
    response_model=CatalogReadResponse,
    dependencies=[Depends(require_permissions("materials.catalog.read"))],
    summary="Каталог: категории, позиции и связи",
    responses={
        404: MATERIALS_CATALOG_READ_NOT_FOUND,
    },
)
async def get_materials_catalog(
    connection: Annotated[Connection, Depends(get_connection)],
    is_active_materials: Annotated[bool | None, Query(description="Фильтр по активности материала")] = None,
    is_active_warehouse: Annotated[bool | None, Query(description="Учитывать только склады с заданной активностью")] = None,
    warehouse_id: Annotated[int | None, Query(ge=1, description="Только материалы на указанном складе")] = None,
):
    if warehouse_id is not None:
        warehouse_ok = await repositories.warehouse_exists(connection, warehouse_id)

        if not warehouse_ok:
            raise APIException(
                status_code=404,
                code="WAREHOUSE_NOT_FOUND",
                message="Склад не найден",
            )

    categories = await repositories.fetch_catalog_categories(connection)
    materials = await repositories.fetch_catalog_materials(connection, is_active_materials, warehouse_id, is_active_warehouse)

    link_rows = await repositories.fetch_catalog_category_material_links(connection, [row['id'] for row in materials])
    subcategory_link_rows = await repositories.fetch_catalog_category_subcategory_links(connection)

    return CatalogReadResponse.model_validate(
        {
            'categories': [dict(x) for x in categories],
            'materials': [
                {
                    **x,
                    'unit': {
                        'id': x['unit_id'],
                        'name': x['unit_name'],
                        'short_name': x['unit_short_name']
                    }
                } for x in materials
            ],
            'category_material_relations': [dict(x) for x in link_rows],
            'category_subcategory_relations': [dict(x) for x in subcategory_link_rows],
        }
    )
