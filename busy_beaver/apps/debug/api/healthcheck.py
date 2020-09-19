import logging

from flask import blueprints, jsonify

logger = logging.getLogger(__name__)
healthcheck_bp = blueprints.Blueprint("healthcheck", __name__)


@healthcheck_bp.route("/healthcheck", methods=["GET"])
def health_check():
    return jsonify({"ping": "pong"})


@healthcheck_bp.route("/healthcheck-logged", methods=["GET"])
def health_check_logged():
    logger.info("Hit healthcheck")
    return jsonify({"ping": "pong"})
