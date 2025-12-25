"""HTTP通信関係の処理をする
"""
from __future__ import annotations
from dataclasses import dataclass
import requests


@dataclass
class MosResponse:
    """MOSからのレスポンスをまとめて持つクラス
    """
    status_code: int    #HTTPステータスコード
    raw_json: object    #JSONとしてパースしたレスポンス

    @property
    def is_error(self) -> bool:
        """errorCode の有無でエラー判定する
        
        :param self: クライアント
        :return: エラーかどうか
        :rtype: bool
        """
        return isinstance(self.raw_json, dict) and "errorCode" in self.raw_json

class MosClient:
    """/api/orders への通信を引き受ける
    """

    def __init__(self, base_url: str, timeout_sec: float = 10.0):
        """URL結合時の二重スラッシュ防止/通信ハングを防ぐためのタイムアウト秒
        
        :param self: クライアント
        :param base_url: 接続先
        :type base_url: str
        :param timeout_sec: タイムアウト
        :type timeout_sec: float
        """
        self.base_url = base_url.rstrip("/")
        self.timeout_sec = timeout_sec

    def post_orders(self, payload):
        """/api/orders に POST するメソッド
        
        :param self: クライアント
        :param payload: リクエスト
        """
        url = f"{self.base_url}/api/orders"
        r = requests.post(url, json=payload, timeout=self.timeout_sec)

        #JSONとして解釈できないレスポンスは擬似エラー扱いする
        try:
            data = r.json()
        except Exception:
            data = {"errorCode": "INVALID_JSON_FORMAT", "message": "Response is not valid JSON."}
            
        return MosResponse(status_code=r.status_code, raw_json=data)
