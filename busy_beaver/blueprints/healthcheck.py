from flask import jsonify
from flask import blueprints

healthcheck_bp = blueprints.Blueprint("healthcheck", __name__)


@healthcheck_bp.route("/healthcheck", methods=["GET"])
def health_check():
    return jsonify({"ping": "pong"})
