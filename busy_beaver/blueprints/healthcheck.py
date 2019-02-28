from flask import jsonify
from flask import blueprints

healthcheck_bp = blueprints.Blueprint('health_check', __name__)


@healthcheck_bp.route('/health_check', methods=['GET'])
def health_check():
    return jsonify({"ping": "pong"})
