from flask import blueprints

web_bp = blueprints.Blueprint("web", __name__)

from . import views  # noqa isort:skip
