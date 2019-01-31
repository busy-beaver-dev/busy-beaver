import logging
import time
from .. import api
from .decorators import authentication_required

logger = logging.getLogger(__name__)


class HelloWorldResource:
    """For testing purposes"""

    async def on_get(self, req, resp):
        logger.info("[Busy-Beaver] Hit hello world endpoint", extra={"test": "payload"})
        resp.media = {"Hello": "World"}


class GoodbyeWorldResource:
    """For testing purposes, part deux"""

    @authentication_required
    async def on_get(self, req, resp, user):
        resp.media = {"See You": "Space Cowboy"}


@api.background.task
def debug(s=2, *, data):
    time.sleep(s)
    print("slept!")
