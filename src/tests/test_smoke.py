"""MOS APIが最低限守るべき代表的なケースをすべて満たしているかを確認するスモークテスト
"""
import os
import pytest
from mos_test.client import MosClient
from mos_test.validators import validate_orders_response, validate_error_response
from mos_test.suites import load_smoke_cases


BASE_URL = os.environ.get("MOS_BASE_URL", "http://localhost:8080")

@pytest.mark.parametrize("case", load_smoke_cases(), ids=lambda c: c["id"])
def test_smoke(case):
    """テストケースを判断する
    
    :param case: suites.pyから来た1テストケース
    :type case: dict[str, Any]
    """

    #テスト用の HTTP クライアントを生成
    client = MosClient(BASE_URL)

    #POST /api/orders に投げる
    resp = client.post_orders(case["request"])

    #期待値の取り出し
    exp = case["expect"]

    #エラーケースの検証
    if exp.get("is_error"):
        validate_error_response(resp.raw_json)
        assert resp.raw_json["errorCode"] == exp["errorCode"]
    #正常ケースの検証
    else:
        validate_orders_response(resp.raw_json)
