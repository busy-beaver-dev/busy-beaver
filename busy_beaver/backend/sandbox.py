import logging
import time
from .. import api
from .decorators import authentication_required

logger = logging.getLogger(__name__)


class HelloWorldResource:
    """For testing purposes"""

    @authentication_required
    async def on_get(self, req, resp, user, *, greeting):
        logger.info("[Busy-Beaver] Hit hello world endpoint", extra={"test": "payload"})
        resp.media = {"Hello": f"World {greeting}"}


class GoodbyeWorldResource:
    """For testing purposes, part deux"""

    async def on_get(self, req, resp):
        resp.media = {"See You": "Space Cowboy"}


@api.background.task
def debug(s=2, *, data):
    time.sleep(s)
    print("slept!")
