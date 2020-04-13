import logging

from flask import blueprints, jsonify

from busy_beaver.extensions import talisman

logger = logging.getLogger(__name__)
healthcheck_bp = blueprints.Blueprint("healthcheck", __name__)


@healthcheck_bp.route("/healthcheck", methods=["GET"])
@talisman(force_https=False)
def health_check():
    return jsonify({"ping": "pong"})


@healthcheck_bp.route("/healthcheck-logged", methods=["GET"])
@talisman(force_https=False)
def health_check_logged():
    logger.info("Hit healthcheck")
    return jsonify({"ping": "pong"})
