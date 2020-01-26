import logging

from flask import blueprints, jsonify

logger = logging.getLogger(__name__)
healthcheck_bp = blueprints.Blueprint("healthcheck", __name__)


@healthcheck_bp.route("/healthcheck", methods=["GET"])
def health_check():
    logger.info("Hit healthcheck")
    return jsonify({"ping": "pong"})
