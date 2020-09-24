from flask import blueprints

cfps_bp = blueprints.Blueprint("cfps", __name__)

from . import views  # noqa isort:skip
