import logging
import time

from .. import api

logger = logging.getLogger(__name__)


class HelloWorldResource:
    """For testing purposes"""

    def on_get(self, req, resp):
        logger.info("[Busy-Beaver] Hit hello world endpoint", extra={"test": "payload"})
        resp.media = {"Hello": "World"}


@api.background.task
def debug(s=2, *, data):
    time.sleep(s)
    print("slept!")
