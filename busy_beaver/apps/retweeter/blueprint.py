from flask import blueprints

twitter_bp = blueprints.Blueprint("twitter", __name__)

from . import cli  # noqa isort:skip
