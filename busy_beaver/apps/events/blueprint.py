from flask import blueprints

events_bp = blueprints.Blueprint("events", __name__)

from . import workflow  # noqa isort:skip
from .event_database import task  # noqa isort:skip
