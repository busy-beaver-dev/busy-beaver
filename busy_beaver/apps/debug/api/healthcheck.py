import logging
from flask import jsonify
from flask import blueprints

logger = logging.getLogger(__name__)
healthcheck_bp = blueprints.Blueprint("healthcheck", __name__)


@healthcheck_bp.route("/healthcheck", methods=["GET"])
def health_check():
    logger.info("Hit healthcheck")
    return jsonify({"ping": "pong"})
