from typing import Annotated

from fastapi import APIRouter, Query

from modules.v1.objects.object.api import router as object_router

router = APIRouter(prefix="/objects", tags=["Управление объектами"])
router.include_router(object_router)


@router.get('/')
async def get_objects(
    category_id: Annotated[int | None, Query(ge=1, description="Индектификатор категории объекта")] = None,
):
    ...


@router.get('/tree')
async def get_objects_tree(
):
    ...
