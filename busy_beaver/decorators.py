import functools
import logging
import re

from flask import request

from .exceptions import NotAuthorized
from .models import ApiUser

logger = logging.getLogger(__name__)
AUTH_STRING = re.compile(r"token (?P<token>.*)")


def authentication_required(roles):
    """Requires request to Authentication header set to 'token {token goes here}'"""
    if not isinstance(roles, list):
        raise ValueError

    def auth_decorator(func):
        @functools.wraps(func)
        def _token_auth(*args, **kwargs):
            if "authorization" not in request.headers:
                logger.error("[Busy-Beaver] No auth header")
                raise NotAuthorized("Missing header: Authorization: 'token {token}'")

            m = AUTH_STRING.match(request.headers["authorization"])
            if not m:
                raise NotAuthorized("Expected header: Authorization: 'token {token}'")

            token = m.group("token")
            api_user: ApiUser = ApiUser.query.filter_by(token=token).first()
            if not api_user:
                logger.error("[Busy-Beaver] Invalid token")
                raise NotAuthorized("Invalid token, contact admin")

            if api_user.role not in roles:
                logger.error("[Busy-Beaver] Unauthorized access of endpoint")
                raise NotAuthorized("Not authorized to access endpoint, contact admin")

            request._internal["user"] = api_user
            return func(*args, **kwargs)

        return _token_auth

    return auth_decorator
