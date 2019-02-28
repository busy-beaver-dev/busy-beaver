from functools import wraps
import logging
import re

from flask import request

from .extensions import db
from .models import ApiUser

logger = logging.getLogger(__name__)
AUTH_STRING = re.compile(r"token (?P<token>.*)")


# TODO... get this sorted
def authentication_required(func):
    @wraps
    def _token_auth(*args, **kwargs):
        if "authorization" not in request.headers:
            logger.error("[Busy-Beaver] No auth header")
            # resp.status_code = 401
            # resp.media = {"message": "Missing header: Authorization: 'token {tkn}'"}
            return

        m = AUTH_STRING.match(request.headers["authorization"])
        if not m:
            # resp.status_code = 401
            # resp.media = {"message": "Expected header: Authenication: 'token {tkn}'"}
            return

        token = m.group("token")
        api_user: ApiUser = db.query(ApiUser).filter_by(token=token).first()
        if not api_user:
            logger.error("[Busy-Beaver] Invalid token")
            # resp.status_code = 401
            # resp.media = {"message": "Invalid token, contact admin"}
            return

        # TODO enchancement
        # if api_user.role not in roles:
        #     logger.error("[Busy-Beaver] Unauthorized access of endpoint")
        #     # resp.status_code = 401
        #     # resp.media = {"message": "Not authorized to access endpoint, contact to admin"}
        #     return

        # TODO put user in request context
        # , user=api_user
        return func(*args, **kwargs)
    return _token_auth
