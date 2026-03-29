from typing import Annotated, Literal

from pydantic import AwareDatetime, BaseModel, Field

from core.models import ObjectUnitStatus, StockOperationType
from core.schemes import Pagination


class ReceiptDetailModel(BaseModel):
    supplier_id: Annotated[int, Field(ge=1, description="Идентификатор поставщика")]


class ReceiptUnitDetailModel(BaseModel):
    price: Annotated[float | None, Field(ge=0, description="Цена за единицу")] = None


class WriteOffToProductionDetailModel(BaseModel):
    production_order_id: Annotated[int, Field(ge=1, description="Идентификатор производственного заказа")]


class WriteOffToProductionUnitDetailModel(BaseModel):
    pass


class ProductionOutputDetailModel(BaseModel):
    production_order_id: Annotated[int, Field(ge=1, description="Идентификатор производственного заказа")]


class ProductionOutputUnitDetailModel(BaseModel):
    cost_price: Annotated[float | None, Field(ge=0, description="Себестоимость")] = None


class ShipmentDetailModel(BaseModel):
    customer_id: Annotated[int, Field(ge=1, description="Идентификатор клиента")]


class ShipmentUnitDetailModel(BaseModel):
    sale_price: Annotated[float, Field(ge=0, description="Цена продажи")]


class ReturnFromProductionDetailModel(BaseModel):
    production_order_id: Annotated[int, Field(ge=1, description="Идентификатор производственного заказа")]
    reason: Annotated[str | None, Field(description="Причина возврата")] = None


class ReturnFromProductionUnitDetailModel(BaseModel):
    reason: Annotated[str | None, Field(description="Причина возврата")] = None


class InventoryAdjustmentDetailModel(BaseModel):
    inventory_date: Annotated[AwareDatetime, Field(description="Дата инвентаризации")]
    reason: Annotated[str | None, Field(description="Причина корректировки")] = None


class InventoryAdjustmentUnitDetailModel(BaseModel):
    reason: Annotated[str | None, Field(description="Причина корректировки")] = None


class ReservationDetailModel(BaseModel):
    order_id: Annotated[int, Field(ge=1, description="Идентификатор заказа")]


class ReservationUnitDetailModel(BaseModel):
    pass


class ReturnToSupplierDetailModel(BaseModel):
    supplier_id: Annotated[int, Field(ge=1, description="Идентификатор поставщика")]
    reason: Annotated[str | None, Field(description="Причина возврата")] = None


class ReturnToSupplierUnitDetailModel(BaseModel):
    reason: Annotated[str | None, Field(description="Причина возврата")] = None


class ReturnFromCustomerDetailModel(BaseModel):
    customer_id: Annotated[int, Field(ge=1, description="Идентификатор клиента")]
    reason: Annotated[str | None, Field(description="Причина возврата")] = None


class ReturnFromCustomerUnitDetailModel(BaseModel):
    reason: Annotated[str | None, Field(description="Причина возврата")] = None
    condition: Annotated[str | None, Field(description="Состояние товара")] = None


class TransferDetailModel(BaseModel):
    comment: Annotated[str | None, Field(description="Комментарий к перемещению")] = None


class TransferUnitDetailModel(BaseModel):
    pass


class BaseOperation[T: StockOperationType, D: BaseModel, U: BaseModel](BaseModel):
    id: Annotated[int, Field(ge=1, description="Идентификатор операции")]
    type: Annotated[T, Field(description="Тип операции")]
    name: Annotated[str, Field(description="Название операции")]
    user_id: Annotated[int, Field(ge=1, description="Идентификатор пользователя")]
    created_at: Annotated[AwareDatetime, Field(description="Время создания операции")]

    detail: Annotated[D, Field(description="Детали операции")]
    units: Annotated[list[BaseOperationUnit[U]], Field(description="Единицы операции")] = []


class BaseOperationUnit[T: BaseModel](BaseModel):
    id: Annotated[int, Field(ge=1, description="Идентификатор единицы операции")]
    operation_id: Annotated[int, Field(ge=1, description="Идентификатор операции")]
    object_unit_id: Annotated[int, Field(ge=1, description="Идентификатор единицы объекта")]
    old_warehouse_id: Annotated[int | None, Field(ge=1, description="Идентификатор старого склада")] = None
    new_warehouse_id: Annotated[int | None, Field(ge=1, description="Идентификатор нового склада")] = None
    old_status: Annotated[ObjectUnitStatus | None, Field(description="Старый статус")] = None
    new_status: Annotated[ObjectUnitStatus | None, Field(description="Новый статус")] = None

    detail: Annotated[T, Field(description="Детали единицы операции")]


OperationType = (
    BaseOperation[
        Literal[StockOperationType.RECEIPT],
        ReceiptDetailModel,
        ReceiptUnitDetailModel
    ] |
    BaseOperation[
        Literal[StockOperationType.WRITE_OFF_TO_PRODUCTION],
        WriteOffToProductionDetailModel,
        WriteOffToProductionUnitDetailModel
    ] |
    BaseOperation[
        Literal[StockOperationType.PRODUCTION_OUTPUT],
        ProductionOutputDetailModel,
        ProductionOutputUnitDetailModel
    ] |
    BaseOperation[
        Literal[StockOperationType.SHIPMENT],
        ShipmentDetailModel,
        ShipmentUnitDetailModel
    ] |
    BaseOperation[
        Literal[StockOperationType.RETURN_FROM_PRODUCTION],
        ReturnFromProductionDetailModel,
        ReturnFromProductionUnitDetailModel
    ] |
    BaseOperation[
        Literal[StockOperationType.INVENTORY_ADJUSTMENT],
        InventoryAdjustmentDetailModel,
        InventoryAdjustmentUnitDetailModel
    ] |
    BaseOperation[
        Literal[StockOperationType.RESERVATION],
        ReservationDetailModel,
        ReservationUnitDetailModel
    ] |
    BaseOperation[
        Literal[StockOperationType.RETURN_TO_SUPPLIER],
        ReturnToSupplierDetailModel,
        ReturnToSupplierUnitDetailModel
    ] |
    BaseOperation[
        Literal[StockOperationType.RETURN_FROM_CUSTOMER],
        ReturnFromCustomerDetailModel,
        ReturnFromCustomerUnitDetailModel
    ] |
    BaseOperation[
        Literal[StockOperationType.TRANSFER_BETWEEN_WAREHOUSES],
        TransferDetailModel,
        TransferUnitDetailModel
    ]
)


class OperationsReadResponse(BaseModel):
    operations: Annotated[list[OperationType], Field(description="Список операций")]
    pagination: Annotated[Pagination, Field(description="Информация о пагинации")]
