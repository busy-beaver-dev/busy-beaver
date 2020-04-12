from flask import blueprints

github_bp = blueprints.Blueprint("github", __name__)

from . import api  # noqa isort:skip
from . import summary  # noqa isort:skip
