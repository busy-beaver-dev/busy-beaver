from flask import blueprints

twitter_bp = blueprints.Blueprint("twitter", __name__)

from . import task  # noqa isort:skip
