from typing import Annotated

from everbase import Connection
from fastapi import APIRouter, Body, Depends, Path

from core.exceptions import APIException
from core.methods import get_connection, require_permissions
from modules.resources.resource import repositories
from modules.resources.resource.responses import RESOURCE_NOT_FOUND
from modules.resources.resource.schemes import ResourceCreate, ResourceCreateResponse, ResourceUpdate
from modules.resources.schemes import resource_read_adapter, ResourceRead

router = APIRouter()


@router.post(
    "/",
    response_model=ResourceCreateResponse,
    status_code=201,
    dependencies=[Depends(require_permissions('resource.create'))],
    summary="Создать новый ресурс"
)
async def create_resource(
    connection: Annotated[Connection, Depends(get_connection)],
    payload: Annotated[ResourceCreate, Body()]
):
    resource_id = await repositories.create_resource(connection, payload)
    return ResourceCreateResponse(id=resource_id)


@router.get(
    "/{resource_id}",
    response_model=ResourceRead,
    dependencies=[Depends(require_permissions('resource.read'))],
    summary="Получить информацию о ресурсе",
    responses={
        404: RESOURCE_NOT_FOUND
    }
)
async def get_resource(
    connection: Annotated[Connection, Depends(get_connection)],
    resource_id: Annotated[int, Path(ge=1, description="Идентификатор ресурса")]
):
    resource = await repositories.get_resource_by_id(connection, resource_id)

    if resource is None:
        raise APIException(
            status_code=404,
            code="RESOURCE_NOT_FOUND",
            message="Ресурс не найден"
        )

    return resource_read_adapter.validate_python(dict(resource))


@router.put(
    "/{resource_id}",
    response_model=None,
    status_code=204,
    dependencies=[Depends(require_permissions('resource.update'))],
    summary="Обновить информацию о ресурсе",
    responses={
        404: RESOURCE_NOT_FOUND
    }
)
async def update_resource(
    connection: Annotated[Connection, Depends(get_connection)],
    resource_id: Annotated[int, Path(ge=1, description="Идентификатор ресурса")],
    payload: Annotated[ResourceUpdate, Body()]
):
    resource = await repositories.get_resource_by_id(connection, resource_id)

    if resource is None:
        raise APIException(
            status_code=404,
            code="RESOURCE_NOT_FOUND",
            message="Ресурс не найден"
        )

    await repositories.update_resource(connection, resource_id, payload)
