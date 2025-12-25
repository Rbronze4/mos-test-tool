"""ハッシュ生成のルールを定義する
"""
from __future__ import annotations
import hashlib
from typing import Any, Dict, List, Tuple


def _norm(v: Any) -> str:
    """ハッシュ用に値を安定した文字列へ正規化する
    
    :param v: クライアント
    :type v: Any
    :return: 文字列
    :rtype: str
    """

    #nullは空文字として扱う
    if v is None:
        return ""
    
    #PythonのTrue/FalseをJSON表現（true/false）に揃える
    if isinstance(v, bool):
        return "true" if v else "false"
    
    return str(v)


def compute_order_hash_v1(order: Dict[str, Any]) -> str:
    """注文データからSHA-256ハッシュを生成する
    
    ハッシュ仕様：
        - SHA-256 16進小文字
        - 正規文字列：v1|storeNo|customerId|entryTime|itemsJoined
        - itemは（orderTime、menuId、unitPrice、orderQty）でソートする
        - itemは、orderTime、menuId、unitPrice、taxRate、orderQty、offerQty としてエンコードする
        - categoryIdを含めない

    :param order: 注文データ
    :type order: Dict[str, Any]
    :return: ハッシュ
    :rtype: str
    """

    #文字列表現を正規化
    store_no = _norm(order.get("storeNo"))
    customer_id = _norm(order.get("customerId"))
    entry_time = _norm(order.get("entryTime"))

    #itemsがnull/未設定でも落ちないよう空配列にする
    items: List[Dict[str, Any]] = list(order.get("items") or [])

    def sort_key(it: Dict[str, Any]) -> Tuple:
        """itemsの順序依存を排除するため、仕様で定めたキー順にソートする
        
        :param it: クライアント
        :type it: Dict[str, Any]
        :return: ソートされたキー
        :rtype: Tuple
        """
        return (
            _norm(it.get("orderTime")),
            _norm(it.get("menuId")),
            _norm(it.get("unitPrice")),
            _norm(it.get("orderQty")),
        )

    items_sorted = sorted(items, key=sort_key)

    item_parts = []     #itemsを文字列にしたものを溜めるリスト

    for it in items_sorted:
        part = ",".join([
            _norm(it.get("orderTime")),
            _norm(it.get("menuId")),
            _norm(it.get("unitPrice")),
            _norm(it.get("taxRate")),
            _norm(it.get("orderQty")),
            _norm(it.get("offerQty")),
        ])
        item_parts.append(part)

    #複数itemを区切り文字';'で結合してitemsJoinedを作る
    items_joined = ";".join(item_parts)

    #カノニカル文字列を生成
    canonical = f"v1|{store_no}|{customer_id}|{entry_time}|{items_joined}"

    #UTF-8でSHA-256を計算し、16進小文字64桁で返す
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
