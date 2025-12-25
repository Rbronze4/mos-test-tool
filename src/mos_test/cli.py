"""エントリーポイント
"""

from __future__ import annotations

import os
import typer
from rich import print
from rich.console import Console

from mos_test.client import MosClient
from mos_test.validators import validate_orders_response, validate_error_response
from mos_test.hash_rules import compute_order_hash_v1
from mos_test.suites import load_smoke_cases

#CLI初期化
app = typer.Typer(add_completion=False)
console = Console()

def _base_url(base_url: str | None) -> str:
    """実行環境ごとに接続先を切り替えられるよう優先順位で決定する関数

    優先順位は CLI引数 > 環境変数 > デフォルト
    
    :param base_url: 接続先
    :type base_url: str | None
    :return: 決定された接続先
    :rtype: str
    """
    return base_url or os.environ.get("MOS_BASE_URL", "http://localhost:8080")

def _mask_from_flags(flags: list[int] | None) -> int | None:
    """ billStatusをビットマスク化する関数
    
    :param flags: billStatus(1/2/4/8)
    :type flags: list[int] | None
    :return: ビットマスク化されたbillStatus
    :rtype: int | None
    """

    #CLIでbill_flag未指定の場合は None を返す（APIでは billStatus:null = 全会計状況）
    if not flags:
        return None
    
    #指定されたフラグをビットORで合成してビットマスクを作る
    mask = 0
    for f in flags:
        mask |= int(f)
    return mask


@app.command()
def getOrders(
    base_url: str = typer.Option(None, help="MOS base URL (or set MOS_BASE_URL)"),
    from_time: str = typer.Option(..., "--from", help="YYYY-MM-DDThh:mm:ss"),
    to_time: str = typer.Option(..., "--to", help="YYYY-MM-DDThh:mm:ss"),
    customer_id: str | None = typer.Option(None, "--customer-id", help="e.g. AA0001 (omit => null)"),
    bill_flag: list[int] = typer.Option(
        None,
        "--bill-flag",
        help="Billing status flags (bit): 1,2,4,8. Can specify multiple. Omit => null (all).",
    ),
):
    """getOrdersを呼び出してスキーマ/条件/ハッシュを検証する
    
    :param base_url: 接続先
    :type base_url: str
    :param from_time: 取得対象日時の開始日時
    :type from_time: str
    :param to_time: 取得対象日時の終了日時
    :type to_time: str
    :param customer_id: 顧客ID。未指定は null として送信し、会計状況での絞り込みを行わない。
    :type customer_id: str | None
    :param bill_flag: billStatus
    :type bill_flag: list[int]
    """

    #接続先URLを確定してHTTPクライアントを作る
    client = MosClient(_base_url(base_url))

    #複数フラグ → ビットマスク int へ変換
    mask = _mask_from_flags(bill_flag)

    #getOrders リクエストを生成（Noneはnullとして送信）
    payload = [{
        "method": "getOrders",
        "customerId": customer_id,   #None => null
        "fromTime": from_time,
        "toTime": to_time,
        "billStatus": mask,          #bitmask か null
    }]

    #POST /api/orders に投げる
    resp = client.post_orders(payload)
    console.rule("[bold]Response[/bold]")

    #返却JSONをそのまま表示（トラブル時の調査用）
    print(resp.raw_json)

    #errorCodeがあればエラーとして扱い、エラーレスポンス形式が仕様準拠か検証する
    if resp.is_error:
        validate_error_response(resp.raw_json)
        raise typer.Exit(code=1)

    #注文配列の中身を検証
    validate_orders_response(
        resp.raw_json,
        expected_customer_id=customer_id,
        expected_bill_status_mask=mask,  #bitmask か None
        from_time=from_time,
        to_time=to_time,
    )

    #hashを再計算し、MOS返却hashと一致するか確認
    mismatches = []
    for o in resp.raw_json:
        expected = compute_order_hash_v1(o)
        if o.get("hash") != expected:
            mismatches.append((o.get("hash"), expected, o.get("storeNo"), o.get("customerId")))
    if mismatches:
        console.rule("[bold red]Hash mismatch[/bold red]")
        for actual, expected, st, cid in mismatches:
            print({"storeNo": st, "customerId": cid, "actual": actual, "expected": expected})
        raise typer.Exit(code=2)

    console.rule("[bold green]OK[/bold green]")


@app.command()
def updateStatus(
    base_url: str = typer.Option(None, help="MOS base URL (or set MOS_BASE_URL)"),
    hash_value: str = typer.Option(..., "--hash", help="Order hash"),
    bill_status: int = typer.Option(..., "--bill-status", help="One of 1,2,4,8 (single status)"),
):
    """updateStatus を呼び出して、エラー/成功応答を検証
    
    :param base_url: 接続先
    :type base_url: str
    :param hash_value: ハッシュ
    :type hash_value: str
    :param bill_status: updateStatusは単一値（1/2/4/8）のみ許容。getOrdersのmaskとは扱いが異なる。
    :type bill_status: int
    """

    #接続先URLを確定してHTTPクライアントを作る
    client = MosClient(_base_url(base_url))

    #updateStatus リクエストを生成
    payload = {
        "method": "updateStatus",
        "hash": hash_value,
        "billStatus": bill_status,
    }

    #POST /api/orders に投げる
    resp = client.post_orders(payload)
    console.rule("[bold]Response[/bold]")

    #返却JSONをそのまま表示（トラブル時の調査用）
    print(resp.raw_json)

    #errorCodeがあればエラーとして扱い、エラーレスポンス形式が仕様準拠か検証する
    if resp.is_error:
        validate_error_response(resp.raw_json)
        raise typer.Exit(code=1)

    console.rule("[bold green]OK[/bold green]")


@app.command()
def smoke(
    base_url: str = typer.Option(None, help="MOS base URL (or set MOS_BASE_URL)"),
):
    """スモーク実行
    
    :param base_url: 接続先
    :type base_url: str
    """

    #接続先URLを確定してHTTPクライアントを作る
    client = MosClient(_base_url(base_url))

    #suites.pyからテストケースを読み込む
    cases = load_smoke_cases()

    failures = 0    #失敗数カウント

    for c in cases:
        console.rule(f"[bold]{c['id']} {c['name']}[/bold]")
        resp = client.post_orders(c["request"])
        print(resp.raw_json)

        #エラーが期待されるかどうかで分岐
        exp = c["expect"]
        if exp.get("is_error", False):
            #エラー期待の場合
            try:
                validate_error_response(resp.raw_json)
                if resp.raw_json.get("errorCode") != exp["errorCode"]:
                    raise AssertionError(
                        f"errorCode expected={exp['errorCode']} actual={resp.raw_json.get('errorCode')}"
                    )
            except Exception as e:
                failures += 1
                print(f"[red]FAIL[/red] {e}")
                continue
            print("[green]OK[/green]")
        else:
            #正常期待の場合
            try:
                validate_orders_response(resp.raw_json)
            except Exception as e:
                failures += 1
                print(f"[red]FAIL[/red] {e}")
                continue
            print("[green]OK[/green]")

    #1件でも失敗がある場合はexit code1
    if failures:
        print(f"[bold red]{failures} failures[/bold red]")
        raise typer.Exit(code=1)

    #全て成功
    print("[bold green]All smoke tests passed[/bold green]")
