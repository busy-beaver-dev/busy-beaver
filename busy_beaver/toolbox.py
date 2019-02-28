from datetime import datetime, timedelta
import json

from flask import Response
from marshmallow import ValidationError
import pytz

from .exceptions import SerializationError, DeserializationError


def utc_now_minus(period: timedelta):
    return pytz.utc.localize(datetime.utcnow()) - period


def make_response(
    status_code: int = 200, *, headers: dict = {}, data: dict = {}, error: dict = {}
):
    """Build and send response"""
    resp = {"data": None, "error": None}
    if data:
        resp["data"] = data
    if error:
        resp["error"] = error

    return Response(
        status=status_code,
        headers=headers,
        content_type="application/json",
        response=json.dumps(resp),
    )


def deserialize_request(schema, data):
    """Wrapper for Marhsmallow's schema.loads"""
    try:
        deserialized_result = schema.load(data)
    except ValidationError as exc:
        raise DeserializationError(payload=exc.messages)
    return deserialized_result


def serialize_response(schema, data):
    """Wrapper for Marhsmallow's schema.dumps"""
    try:
        serialized_result = schema.dumps(data)
    except ValidationError as exc:
        raise SerializationError(payload=exc.messages)
    return serialized_result
