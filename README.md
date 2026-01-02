MOS API Test Tool

概要

    本ツールは、MOS が提供する注文API（getOrders / updateStatus）に対して、
    API仕様どおりに実装されているかを検証するためのテストツールです。
    
    主に以下の観点で検証を行います。
    ・リクエスト／レスポンスの スキーマ検証
    ・入力条件（customerId、日時、billStatus 等）の 仕様準拠確認
    ・エラーコード・エラーメッセージの 仕様準拠確認
    ・注文ハッシュ（SHA-256）の 再計算チェック
    ・代表的なケースをまとめた スモークテスト

    本ツールは、MOS開発者・レジ開発者の双方が共通理解を持つための検証用ツールとして利用することを想定しています。

対象API

    ・getOrders
    ・updateStatus

前提条件

    ・Python 3.10 以上
    ・HTTP通信

インストール

    1. リポジトリの取得
        git clone <repository-url>
        cd mos-api-test-tool

    2. 仮想環境の作成
        python -m venv .venv

        Windows
        .venv\Scripts\Activate

        macOS / Linux
        source .venv/bin/activate

    3. 依存ライブラリのインストール
        pip install -e .

環境変数

    変数名	         説明	                デフォルト
    MOS_BASE_URL	MOS API のベースURL	    http://localhost:8080

    例（Windows PowerShell）：
    $env:MOS_BASE_URL="http://127.0.0.1:8000"

使い方（CLI）

    getOrders
        mos-test getOrders \
        --from 2025-11-24T19:00:00 \
        --to   2025-11-25T01:00:00

    オプション
        オプション	         説明
        --customer-id	    カスタマーID（未指定の場合は null）
        --bill-flag	        会計状況フラグ（1,2,4,8）。複数指定可
        --from	            取得対象開始日時
        --to	            取得対象終了日時

        例（受付中＋未集金を指定）：
            mos-test getOrders \
            --bill-flag 1 \
            --bill-flag 8 \
            --from 2025-11-24T19:00:00 \
            --to   2025-11-25T01:00:00

    updateStatus
        mos-test updateStatus \
        --hash <order-hash> \
        --bill-status 4

    スモークテスト
        代表的な 10〜20 ケースをまとめて実行します。
            mos-test smoke

        ・正常系
        ・パラメータ不正
        ・エラーコード検証
        ・billStatus ビットマスク検証

検証内容の詳細
    
    1. スキーマ検証
        ・必須項目の存在確認
        ・データ型チェック
        ・正規表現チェック
            ・customerId：^[A-Z]{2}[0-9]{4}$
            ・menuId：^[FD][0-9]{3}$
            ・hash：16進数64桁（小文字）

    2. 条件検証
        ・customerId 指定時は 最大1件のみ返却
        ・billStatus 指定時は ビットマスクによるフィルタ
        ・from/to による日時範囲チェック

    3. ハッシュ検証
        MOS が返却する hash について、
        テストツール側で 仕様に基づき再計算を行い、一致することを確認します。
        ハッシュ仕様（v1）
            ・SHA-256（hex 小文字）
            ・カノニカル文字列形式：
                v1|storeNo|customerId|entryTime|itemsJoined
            ・items は以下のキーでソート：
            ・orderTime
            ・menuId
            ・unitPrice
            ・orderQty
            ・categoryId は ハッシュ対象外

最後に

    本ツールは、「仕様書に書かれた内容が実装で守られているか」 を機械的に検証することを目的としています。
    仕様・実装・テストの認識を揃えるための補助ツールとしてご利用ください。


