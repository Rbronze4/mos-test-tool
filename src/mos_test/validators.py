"""正規表現/相互整合/条件を検証する
"""
from __future__ import annotations
import re
from typing import Optional, Any, List

from mos_test.models import Order, ErrorResponse

#正義表現の定義
RE_STORE = re.compile(r"^[A-Z]{2}$")
RE_CUSTOMER = re.compile(r"^[A-Z]{2}[0-9]{4}$")
RE_HASH = re.compile(r"^[0-9a-f]{64}$")
RE_TIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")
RE_MENUID = re.compile(r"^[FD][0-9]{3}$")

ALLOWED_STATUS_SINGLE = {1, 2, 4, 8}            # レスポンスのbillStatusは単一値（1/2/4/8）
ALLOWED_STATUS_MASK_RANGE = set(range(1, 16))   # リクエストのbillStatusはビットマスク（1..15）


def validate_error_response(obj: Any) -> None:
    """エラーレスポンスがErrorResponse形式であることを保証する
    
    :param obj: クライアント
    :type obj: Any
    """
    ErrorResponse.model_validate(obj)


def validate_orders_response(
    obj: Any,
    expected_customer_id: Optional[str] = None,
    expected_bill_status_mask: Optional[int] = None,
    from_time: Optional[str] = None,
    to_time: Optional[str] = None,
) -> List[Order]:
    """正規表現/相互整合/条件を検証する
    
    :param obj: MOSから返ったJSON
    :type obj: Any
    :param expected_customer_id: CLIでcustomerIdを指定した場合に渡す
    :type expected_customer_id: Optional[str]
    :param expected_bill_status_mask: --bill-flagを複数指定した場合に渡す
    :type expected_bill_status_mask: Optional[int]
    :param from_time: 範囲チェック
    :type from_time: Optional[str]
    :param to_time: 範囲チェック
    :type to_time: Optional[str]
    :return: 検証済みOrderのリスト
    :rtype: List[Order]
    """

    #成功時は注文配列（list）という仕様を強制させる
    if not isinstance(obj, list):
        raise AssertionError("Expected list response for success (orders array).")

    #objの各要素をOrderモデルとして検証・変換
    orders = [Order.model_validate(x) for x in obj]

    #スキーマ/フォーマットのチェック
    for o in orders:
        if not RE_STORE.match(o.storeNo):
            raise AssertionError(f"Invalid storeNo format: {o.storeNo}")
        if not RE_CUSTOMER.match(o.customerId):
            raise AssertionError(f"Invalid customerId format: {o.customerId}")
        if not RE_HASH.match(o.hash):
            raise AssertionError(f"Invalid hash format: {o.hash}")
        if not RE_TIME.match(o.entryTime):
            raise AssertionError(f"Invalid entryTime format: {o.entryTime}")
        if o.billStatus not in ALLOWED_STATUS_SINGLE:
            raise AssertionError(f"Invalid billStatus (must be one of {sorted(ALLOWED_STATUS_SINGLE)}): {o.billStatus}")

        #storeNoとcustomerIdの一貫性
        if o.customerId[:2] != o.storeNo:
            raise AssertionError(f"storeNo and customerId prefix mismatch: storeNo={o.storeNo} customerId={o.customerId}")

        #itemsの検証
        for it in o.items:
            if not RE_TIME.match(it.orderTime):
                raise AssertionError(f"Invalid orderTime format: {it.orderTime}")
            if not RE_MENUID.match(it.menuId):
                raise AssertionError(f"Invalid menuId format: {it.menuId}")
            if it.orderQty < 1:
                raise AssertionError("orderQty must be >= 1")
            if it.offerQty < 0:
                raise AssertionError("offerQty must be >= 0")

    #customerId指定の検証
    if expected_customer_id is not None:
        if len(orders) > 1:
            raise AssertionError("customerId specified, but multiple orders returned.")
        if len(orders) == 1 and orders[0].customerId != expected_customer_id:
            raise AssertionError(f"customerId mismatch expected={expected_customer_id} actual={orders[0].customerId}")

    #billStatus mask の検証
    if expected_bill_status_mask is not None:
        if expected_bill_status_mask not in ALLOWED_STATUS_MASK_RANGE:
            raise AssertionError(f"Invalid expected mask (must be 1..15): {expected_bill_status_mask}")
        for o in orders:
            if (o.billStatus & expected_bill_status_mask) == 0:
                raise AssertionError(f"billStatus {o.billStatus} does not match mask {expected_bill_status_mask}")

    #from/to チェックは文字列ベース
    if from_time and to_time:
        for o in orders:
            if not (from_time <= o.entryTime <= to_time):
                raise AssertionError(f"entryTime out of range: {o.entryTime}")

    return orders
