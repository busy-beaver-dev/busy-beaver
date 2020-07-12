from flask import blueprints

events_bp = blueprints.Blueprint("events", __name__)

from . import cli  # noqa isort:skip
