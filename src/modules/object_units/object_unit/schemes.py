from typing import Annotated, Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, Field

from core.models import ObjectUnitStatus, StockOperationType
from core.schemes import Pagination


class BaseOperation[T: StockOperationType, D: BaseModel, U: BaseModel](BaseModel):
    id: Annotated[int, Field(ge=1, description="Идентификатор операции")]

    type: Annotated[T, Field(description="Тип операции")]
    name: Annotated[str, Field(description="Название операции")]
    user_id: Annotated[int, Field(ge=1, description="Идентификатор пользователя")]

    detail: Annotated[D, Field(description="Детали операции")]
    units: Annotated[list[BaseOperationUnit[U]], Field(description="Единицы операции")] = []

    created_at: Annotated[AwareDatetime, Field(description="Время создания операции")]


class BaseOperationUnit[T: BaseModel](BaseModel):
    id: Annotated[int, Field(ge=1, description="Идентификатор единицы операции")]

    operation_id: Annotated[int, Field(ge=1, description="Идентификатор операции")]
    object_unit_id: Annotated[UUID, Field(ge=1, description="Идентификатор единицы объекта")]

    old_warehouse_id: Annotated[int | None, Field(ge=1, description="Идентификатор старого склада")] = None
    new_warehouse_id: Annotated[int | None, Field(ge=1, description="Идентификатор нового склада")] = None
    old_status: Annotated[ObjectUnitStatus | None, Field(description="Старый статус")] = None
    new_status: Annotated[ObjectUnitStatus | None, Field(description="Новый статус")] = None

    detail: Annotated[T, Field(description="Детали единицы операции")]


class ReceiptOperationModel:

    class Detail(BaseModel):
        supplier_id: Annotated[int, Field(ge=1, description="Идентификатор поставщика")]

    class UnitDetail(BaseModel):
        price: Annotated[float | None, Field(ge=0, description="Цена за единицу")] = None


class WriteOffToProductionOperationModel:

    class Detail(BaseModel):
        order_id: Annotated[int, Field(ge=1, description="Идентификатор производственного заказа")]

    class UnitDetail(BaseModel):
        pass


class ProductionOutputOperationModel:

    class Detail(BaseModel):
        order_id: Annotated[int, Field(ge=1, description="Идентификатор производственного заказа")]

    class UnitDetail(BaseModel):
        cost_price: Annotated[float | None, Field(ge=0, description="Себестоимость")] = None


class ShipmentOperationModel:

    class Detail(BaseModel):
        customer_id: Annotated[int, Field(ge=1, description="Идентификатор клиента")]

    class UnitDetail(BaseModel):
        sale_price: Annotated[float, Field(ge=0, description="Цена продажи")]


class ReturnFromProductionOperationModel:

    class Detail(BaseModel):
        order_id: Annotated[int, Field(ge=1, description="Идентификатор производственного заказа")]
        reason: Annotated[str | None, Field(description="Причина возврата")] = None

    class UnitDetail(BaseModel):
        reason: Annotated[str | None, Field(description="Причина возврата")] = None


class InventoryAdjustmentOperationModel:

    class Detail(BaseModel):
        inventory_date: Annotated[AwareDatetime, Field(description="Дата инвентаризации")]
        reason: Annotated[str | None, Field(description="Причина корректировки")] = None

    class UnitDetail(BaseModel):
        reason: Annotated[str | None, Field(description="Причина корректировки")] = None


class ReservationOperationModel:

    class Detail(BaseModel):
        order_id: Annotated[int, Field(ge=1, description="Идентификатор заказа")]

    class UnitDetail(BaseModel):
        pass


class ReturnToSupplierOperationModel:

    class Detail(BaseModel):
        supplier_id: Annotated[int, Field(ge=1, description="Идентификатор поставщика")]
        reason: Annotated[str | None, Field(description="Причина возврата")] = None

    class UnitDetail(BaseModel):
        reason: Annotated[str | None, Field(description="Причина возврата")] = None


class ReturnFromCustomerOperationModel:

    class Detail(BaseModel):
        customer_id: Annotated[int, Field(ge=1, description="Идентификатор клиента")]
        reason: Annotated[str | None, Field(description="Причина возврата")] = None

    class UnitDetail(BaseModel):
        reason: Annotated[str | None, Field(description="Причина возврата")] = None
        condition: Annotated[str | None, Field(description="Состояние товара")] = None


class TransferOperationModel:

    class Detail(BaseModel):
        comment: Annotated[str | None, Field(description="Комментарий к перемещению")] = None

    class UnitDetail(BaseModel):
        pass


OperationType = (
    BaseOperation[
        Literal[StockOperationType.RECEIPT],
        ReceiptOperationModel.Detail,
        ReceiptOperationModel.UnitDetail
    ] |
    BaseOperation[
        Literal[StockOperationType.WRITE_OFF_TO_PRODUCTION],
        WriteOffToProductionOperationModel.Detail,
        WriteOffToProductionOperationModel.UnitDetail
    ] |
    BaseOperation[
        Literal[StockOperationType.PRODUCTION_OUTPUT],
        ProductionOutputOperationModel.Detail,
        ProductionOutputOperationModel.UnitDetail
    ] |
    BaseOperation[
        Literal[StockOperationType.SHIPMENT],
        ShipmentOperationModel.Detail,
        ShipmentOperationModel.UnitDetail
    ] |
    BaseOperation[
        Literal[StockOperationType.RETURN_FROM_PRODUCTION],
        ReturnFromProductionOperationModel.Detail,
        ReturnFromProductionOperationModel.UnitDetail
    ] |
    BaseOperation[
        Literal[StockOperationType.INVENTORY_ADJUSTMENT],
        InventoryAdjustmentOperationModel.Detail,
        InventoryAdjustmentOperationModel.UnitDetail
    ] |
    BaseOperation[
        Literal[StockOperationType.RESERVATION],
        ReservationOperationModel.Detail,
        ReservationOperationModel.UnitDetail
    ] |
    BaseOperation[
        Literal[StockOperationType.RETURN_TO_SUPPLIER],
        ReturnToSupplierOperationModel.Detail,
        ReturnToSupplierOperationModel.UnitDetail
    ] |
    BaseOperation[
        Literal[StockOperationType.RETURN_FROM_CUSTOMER],
        ReturnFromCustomerOperationModel.Detail,
        ReturnFromCustomerOperationModel.UnitDetail
    ] |
    BaseOperation[
        Literal[StockOperationType.TRANSFER_BETWEEN_WAREHOUSES],
        TransferOperationModel.Detail,
        TransferOperationModel.UnitDetail
    ]
)


class OperationsReadResponse(BaseModel):
    operations: Annotated[list[OperationType], Field(description="Список операций")]
    pagination: Annotated[Pagination, Field(description="Информация о пагинации")]


class ObjectUnitRead(BaseModel):
    id: Annotated[int, Field(ge=1, description="Идентификатор единицы объекта")]
    object_id: Annotated[int, Field(ge=1, description="Идентификатор объекта")]
    warehouse_id: Annotated[int | None, Field(ge=1, description="Идентификатор склада")] = None
    status: Annotated[ObjectUnitStatus, Field(description="Статус единицы объекта")]
    created_at: Annotated[AwareDatetime, Field(description="Время создания единицы объекта")]
