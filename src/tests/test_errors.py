"""MOSをテストするためのツールが、エラーを正しくエラーとして扱えているかを検証するテスト
"""
import os
from mos_test.client import MosClient
from mos_test.validators import validate_error_response


BASE_URL = os.environ.get("MOS_BASE_URL", "http://localhost:8080")

def test_error_schema():
    """pytestが自動検出するテスト関数
    """

    #テスト用の HTTP クライアントを生成
    client = MosClient(BASE_URL)

    #意図的に壊したレスポンス
    payload = [{
        "method": "getOrders",
        "storeNo": "AA",
        "customerId": None,
        # fromTime を意図的に欠落させる
        "toTime": "2025-11-25T01:00:00",
        "billStatus": None,
    }]

    #POST /api/orders に投げる
    resp = client.post_orders(payload)

    #エラースキーマ検証
    validate_error_response(resp.raw_json)
