import logging
import re

from flask import request

from .models import ApiUser
from .toolbox import make_response

logger = logging.getLogger(__name__)
AUTH_STRING = re.compile(r"token (?P<token>.*)")


# TODO... get this sorted
def authentication_required(roles):
    """Requires request to Authentication header set to 'token {token goes here}'"""
    if not isinstance(roles, list):
        raise ValueError

    def auth_decorator(func):
        def _token_auth(*args, **kwargs):
            if "authorization" not in request.headers:
                logger.error("[Busy-Beaver] No auth header")
                data = {"message": "Missing header: Authorization: 'token {token}'"}
                return make_response(401, error=data)

            m = AUTH_STRING.match(request.headers["authorization"])
            if not m:
                data = {"message": "Expected header: Authorization: 'token {token}'"}
                return make_response(401, error=data)

            token = m.group("token")
            api_user: ApiUser = ApiUser.query.filter_by(token=token).first()
            if not api_user:
                logger.error("[Busy-Beaver] Invalid token")
                data = {"message": "Invalid token, contact admin"}
                return make_response(401, error=data)

            # TODO enchancement
            if api_user.role not in roles:
                logger.error("[Busy-Beaver] Unauthorized access of endpoint")
                data = {"message": "Not authorized to access endpoint, contact to admin"}
                return make_response(401, error=data)

            # TODO put user in request context
            # , user=api_user
            return func(*args, **kwargs)
        # Not sure why we need this line... can funtools fix it?
        # https://stackoverflow.com/questions/17256602/assertionerror-view-function-mapping-is-overwriting-an-existing-endpoint-functi
        _token_auth.__name__ = func.__name__
        return _token_auth
    return auth_decorator
