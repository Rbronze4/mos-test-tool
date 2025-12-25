"""テストシナリオ
"""
from __future__ import annotations

def load_smoke_cases():
    """テストケース
    """
    return [
        {
            "id": "S01",
            "name": "getOrders: customerId=null, billStatus=null (all statuses)",
            "request": [{
                "method": "getOrders",
                "customerId": None,
                "fromTime": "2025-11-24T19:00:00",
                "toTime": "2025-11-25T01:00:00",
                "billStatus": None,
            }],
            "expect": {"is_error": False},
        },
        {
            "id": "S02",
            "name": "getOrders: billStatus mask=9 (example composite)",
            "request": [{
                "method": "getOrders",
                "customerId": None,
                "fromTime": "2025-11-24T19:00:00",
                "toTime": "2025-11-25T01:00:00",
                "billStatus": 9,
            }],
            "expect": {"is_error": False},
        },
        {
            "id": "S03",
            "name": "getOrders: customerId specified (single result expected)",
            "request": [{
                "method": "getOrders",
                "customerId": "AA0001",
                "fromTime": "2025-11-24T19:00:00",
                "toTime": "2025-11-25T01:00:00",
                "billStatus": None,
            }],
            "expect": {"is_error": False},
        },
        {
            "id": "S04",
            "name": "updateStatus: ORDER_NOT_FOUND for unknown hash",
            "request": {
                "method": "updateStatus",
                "hash": "0" * 64,
                "billStatus": 1
            },
            "expect": {"is_error": True, "errorCode": "ORDER_NOT_FOUND"},
        },
        {
            "id": "S05",
            "name": "invalid method",
            "request": [{
                "method": "unknownMethod",
                "customerId": None,
                "fromTime": "2025-11-24T19:00:00",
                "toTime": "2025-11-25T01:00:00",
                "billStatus": None,
            }],
            "expect": {"is_error": True, "errorCode": "UNSUPPORTED_METHOD_TYPE"},
        },
        {
            "id": "S06",
            "name": "missing parameter: fromTime missing",
            "request": [{
                "method": "getOrders",
                "customerId": None,
                "toTime": "2025-11-25T01:00:00",
                "billStatus": None,
            }],
            "expect": {"is_error": True, "errorCode": "MISSING_PARAMETER"},
        },
        {
            "id": "S07",
            "name": "invalid time format",
            "request": [{
                "method": "getOrders",
                "customerId": None,
                "fromTime": "2025/11/24 19:00",
                "toTime": "2025-11-25T01:00:00",
                "billStatus": None,
            }],
            "expect": {"is_error": True, "errorCode": "INVALID_PARAMETER"},
        },
        {
            "id": "S08",
            "name": "time range inverted",
            "request": [{
                "method": "getOrders",
                "customerId": None,
                "fromTime": "2025-11-25T01:00:00",
                "toTime": "2025-11-24T19:00:00",
                "billStatus": None,
            }],
            "expect": {"is_error": True, "errorCode": "INVALID_PARAMETER"},
        },
        {
            "id": "S09",
            "name": "invalid customerId format",
            "request": [{
                "method": "getOrders",
                "customerId": "A0001",
                "fromTime": "2025-11-24T19:00:00",
                "toTime": "2025-11-25T01:00:00",
                "billStatus": None,
            }],
            "expect": {"is_error": True, "errorCode": "INVALID_PARAMETER"},
        },
        {
            "id": "S10",
            "name": "getOrders: invalid billStatus=0 (mask must be 1..15)",
            "request": [{
                "method": "getOrders",
                "customerId": None,
                "fromTime": "2025-11-24T19:00:00",
                "toTime": "2025-11-25T01:00:00",
                "billStatus": 0,
            }],
            "expect": {"is_error": True, "errorCode": "INVALID_PARAMETER"},
        },
        {
            "id": "S11",
            "name": "getOrders: invalid billStatus=16 (out of range)",
            "request": [{
                "method": "getOrders",
                "customerId": None,
                "fromTime": "2025-11-24T19:00:00",
                "toTime": "2025-11-25T01:00:00",
                "billStatus": 16,
            }],
            "expect": {"is_error": True, "errorCode": "INVALID_PARAMETER"},
        },
        {
            "id": "S12",
            "name": "updateStatus: invalid billStatus (not one of 1/2/4/8)",
            "request": {
                "method": "updateStatus",
                "hash": "0" * 64,
                "billStatus": 9
            },
            "expect": {"is_error": True, "errorCode": "INVALID_BILL_STATUS"},
        },
        {
            "id": "S13",
            "name": "updateStatus: missing hash",
            "request": {
                "method": "updateStatus",
                "billStatus": 1
            },
            "expect": {"is_error": True, "errorCode": "MISSING_PARAMETER"},
        },
        {
            "id": "S14",
            "name": "getOrders: billStatus mask=15 (all flags explicitly)",
            "request": [{
                "method": "getOrders",
                "customerId": None,
                "fromTime": "2025-11-24T19:00:00",
                "toTime": "2025-11-25T01:00:00",
                "billStatus": 15,
            }],
            "expect": {"is_error": False},
        },
        {
            "id": "S15",
            "name": "getOrders: customerId specified + mask=9",
            "request": [{
                "method": "getOrders",
                "customerId": "AA0001",
                "fromTime": "2025-11-24T19:00:00",
                "toTime": "2025-11-25T01:00:00",
                "billStatus": 9,
            }],
            "expect": {"is_error": False},
        },
        {
            "id": "S16",
            "name": "getOrders: missing method",
            "request": [{
                # "method" missing
                "customerId": None,
                "fromTime": "2025-11-24T19:00:00",
                "toTime": "2025-11-25T01:00:00",
                "billStatus": None,
            }],
            "expect": {"is_error": True, "errorCode": "MISSING_PARAMETER"},
        },
    ]
