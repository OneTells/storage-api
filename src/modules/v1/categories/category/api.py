from typing import Annotated

from asyncpg import Record
from fastapi import APIRouter, Body, HTTPException
from sqlalchemy import Select, Update
from sqlalchemy.dialects.postgresql import Insert

from core.models import Category, CategoryObject, CategorySubcategory
from core.objects import database
from core.utils.openapi import INTERNAL_ERROR_RESPONSE
from modules.v1.categories.schemas import (CategoryCreate, CategoryCreateResponse, CategoryIdType, CategoryRead, CategoryUpdate)
CategoryIdType = Annotated[int, Path(ge=1, description="Идентификатор категории")]

CATEGORY_NOT_FOUND_RESPONSE = {
    "description": "Категория не существует",
    "content": {
        "application/json": {
            "example": {"detail": "Категория не существует"}
        }
    }
}

router = APIRouter()


@router.post(
    '/',
    response_model=CategoryCreateResponse,
    status_code=201,
    summary="Создать новую категорию",
    responses={
        201: {"description": "Идентификатор созданной категории"},
    }
)
async def create_category(payload: Annotated[CategoryCreate, Body()]):
    async with database.get_connection() as connection:
        response: Record = await (
            Insert(Category)
            .values(**payload.model_dump())
            .returning(Category.id)
            .fetch_one(connection)
        )

    return {'id': response['id']}


@router.get(
    '/{category_id}',
    response_model=CategoryRead,
    summary="Получить информацию о категории",
    responses={
        200: {"description": "Информация о категории"},
        404: CATEGORY_NOT_FOUND_RESPONSE,
    }
)
async def get_category(category_id: CategoryIdType):
    async with database.get_connection() as connection:
        response = await (
            Select(
                Category.id,
                Category.name,
                Category.description,
                Category.created_at
            )
            .where(Category.id == category_id)
            .fetch_one(connection, model=lambda x: dict(x))
        )

    if response is None:
        raise HTTPException(status_code=404, detail="Категория не существует")

    return response


@router.put(
    '/{category_id}',
    status_code=204,
    summary="Обновить информацию о категории",
    responses={
        204: {"description": "Категория успешно обновлёна"},
        404: CATEGORY_NOT_FOUND_RESPONSE,
    }
)
async def update_category(
    category_id: CategoryIdType,
    payload: Annotated[CategoryUpdate, Body()]
):
    async with database.get_connection() as connection:
        response = await (
            Update(Category)
            .values(**payload.model_dump())
            .where(Category.id == category_id)
            .returning(Category.id)
            .fetch_one(connection)
        )

    if response is None:
        raise HTTPException(status_code=404, detail="Категория не существует")

    return None


@router.delete(
    '/{category_id}',
    status_code=204,
    summary="Удалить категорию",
    responses={
        204: {"description": "Категория успешно удалена"},
        404: CATEGORY_NOT_FOUND_RESPONSE,
        409: {
            "description": "Удаление категории невозможно из-за наличия дочерних категорий или объектов",
            "content": {
                "application/json": {
                    "examples": {
                        "all": {
                            "summary": "Наличие дочерних категорий и объектов",
                            "value": {
                                "detail": "Удаление категории невозможно из-за наличия дочерних категорий и объектов"
                            }
                        },
                        "objects": {
                            "summary": "Наличие дочерних объектов",
                            "value": {
                                "detail": "Удаление категории невозможно из-за наличия дочерних объектов"
                            }
                        },
                        "categories": {
                            "summary": "Наличие дочерних категорий",
                            "value": {
                                "detail": "Удаление категории невозможно из-за наличия дочерних категорий"
                            }
                        }
                    }
                }
            },
        },
    }
)
async def delete_category(category_id: CategoryIdType):
    async with database.get_connection() as connection:
        response: list[bool] = await (
            Select(
                (
                    Select(1)
                    .select_from(Category)
                    .where(Category.id == category_id)
                    .exists()
                ),
                (
                    Select(1)
                    .select_from(CategoryObject)
                    .where(CategoryObject.category_id == category_id)
                    .exists()
                ),
                (
                    Select(1)
                    .select_from(CategorySubcategory)
                    .where(CategorySubcategory.category_id == category_id)
                    .exists()
                )
            )
            .fetch_one(connection, model=lambda x: list(map(bool, x)))
        )

        exists_category, exists_objects, exists_subcategory = response

        if not exists_category:
            raise HTTPException(status_code=404, detail="Категория не существует")

        if exists_objects and exists_subcategory:
            raise HTTPException(
                status_code=409,
                detail="Удаление категории невозможно из-за наличия дочерних категорий и объектов"
            )

        if exists_objects:
            raise HTTPException(
                status_code=409,
                detail="Удаление категории невозможно из-за наличия дочерних объектов"
            )

        if exists_subcategory:
            raise HTTPException(
                status_code=409,
                detail="Удаление категории невозможно из-за наличия дочерних категорий"
            )

        await (
            Delete(Category)
            .where(Category.id == category_id)
            .execute(connection)
        )

    return None
