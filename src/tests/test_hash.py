"""MOSが返却するhashが、仕様どおりに計算されたものであることを検証するテスト
"""
import os
import pytest
from mos_test.client import MosClient
from mos_test.hash_rules import compute_order_hash_v1
from mos_test.validators import validate_orders_response


BASE_URL = os.environ.get("MOS_BASE_URL", "http://localhost:8080")

def test_hash_recompute_on_getorders():
    """getOrdersのレスポンスについてhashを再計算できるかテストする
    """

    #テスト用の HTTP クライアントを生成
    client = MosClient(BASE_URL)

    #getOrdersリクエストを生成
    payload = [{
        "method": "getOrders",
        "storeNo": "AA",
        "customerId": None,
        "fromTime": "2025-11-24T19:00:00",
        "toTime": "2025-11-25T01:00:00",
        "billStatus": None,
    }]

    #POST /api/orders に投げる
    resp = client.post_orders(payload)

    #成功レスポンス検証
    orders = validate_orders_response(resp.raw_json)

    #注文がない場合、失敗として扱わず、スキップして成功とする
    if not orders:
        pytest.skip("No orders returned; cannot validate hash recomputation.")

    #ハッシュ再計算と比較
    for o in resp.raw_json:
        expected = compute_order_hash_v1(o)
        assert o["hash"] == expected
