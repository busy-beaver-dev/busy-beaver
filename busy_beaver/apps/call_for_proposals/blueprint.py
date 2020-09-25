from flask import blueprints

cfps_bp = blueprints.Blueprint("cfps", __name__)

from . import cli  # noqa isort:skip
