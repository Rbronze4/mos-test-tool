"""APIレスポンスの形（構造）を定義する
"""
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ErrorResponse(BaseModel):
    """エラーレスポンス
    validate_error_response() で使われる
    """
    errorCode: str
    message: str
    details: Optional[dict] = None  #任意の補足情報


class Item(BaseModel):
    """注文の1詳細を表す
    """
    #定義していないフィールドが来てもエラーにしない
    model_config = ConfigDict(extra="allow")

    orderTime: str
    menuId: str
    unitPrice: int
    taxRate: int
    orderQty: int
    offerQty: int
    categoryId: Optional[str] = None


class Order(BaseModel):
    """getOrders成功時の1注文を表す
    """

    #定義していないフィールドが来てもエラーにしない
    model_config = ConfigDict(extra="allow")

    hash: str
    storeNo: str
    entryTime: str
    customerId: str
    billStatus: int

    #itemsが未設定/nullでも空配列として扱う
    items: List[Item] = Field(default_factory=list)
