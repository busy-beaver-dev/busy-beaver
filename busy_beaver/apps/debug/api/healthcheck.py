import logging

from flask import blueprints, jsonify

from busy_beaver.extensions import talisman

logger = logging.getLogger(__name__)
healthcheck_bp = blueprints.Blueprint("healthcheck", __name__)


@healthcheck_bp.route("/healthcheck", methods=["GET"])
@talisman(force_https=False)
def health_check():
    logger.info("Hit healthcheck")
    return jsonify({"ping": "pong"})
