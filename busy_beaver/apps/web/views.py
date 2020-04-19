import logging

from flask import jsonify
from flask.views import MethodView

from .blueprint import web_bp

logger = logging.getLogger(__name__)


class HomePageView(MethodView):
    def get(self):
        result = {"ping": "pong"}
        return jsonify(result)


web_bp.add_url_rule("/", view_func=HomePageView.as_view("home"))
