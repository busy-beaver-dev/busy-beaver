import logging
import re
import responder

from .. import db
from ..models import ApiUser

logger = logging.getLogger(__name__)
AUTH_STRING = re.compile(r"token (?P<token>.*)")


def authentication_required(func):
    async def _token_auth(*args, **kwargs):
        req = resp = None
        for arg in args:
            if isinstance(arg, responder.Request):
                req = arg
            if isinstance(arg, responder.Response):
                resp = arg

        if req and resp:
            if "authorization" not in req.headers:
                logger.error("[Busy-Beaver] No auth header")
                resp.status_code = 401
                resp.media = {"message": "Missing header: Authorization: 'token {tkn}'"}
                return

            m = AUTH_STRING.match(req.headers["authorization"])
            if not m:
                resp.status_code = 401
                resp.media = {"message": "Authorization specification: 'token {tkn}'"}
                return

            token = m.group("token")
            api_user: ApiUser = db.query(ApiUser).filter_by(token=token).first()
            if not api_user:
                logger.error("[Busy-Beaver] Invalid token")
                resp.status_code = 401
                resp.media = {"message": "Invalid token, please talk to admin"}
                return

            return await func(*args, **kwargs, user=api_user)
    return _token_auth
