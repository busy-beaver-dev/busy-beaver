from datetime import datetime, timedelta
import json as _json

from flask import Response
import pytz


def utc_now_minus(period: timedelta):
    return pytz.utc.localize(datetime.utcnow()) - period


def make_response(
    status_code: int = 200,
    *,
    headers: dict = None,
    json: dict = None,
    error: dict = None,
):
    """Build and send response"""
    resp = {"data": {}, "error": {}}
    if json:
        resp["data"] = json
    if error:
        resp["error"] = error

    return Response(
        status=status_code,
        headers=headers if headers else {},
        content_type="application/json",
        response=_json.dumps(resp),
    )
