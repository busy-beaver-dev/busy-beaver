import logging

from flask import render_template
from flask.views import View
from flask_login import login_required

from .blueprint import web_bp

logger = logging.getLogger(__name__)


class RenderTemplateView(View):
    """Template View

    Pulled straight from Flask docs:
    - https://flask.palletsprojects.com/en/1.1.x/views/
    """

    def __init__(self, template_name):
        self.template_name = template_name

    def dispatch_request(self):
        return render_template(self.template_name)


web_bp.add_url_rule(
    "/", view_func=RenderTemplateView.as_view("home", template_name="index.html")
)


@web_bp.route("/settings")
@login_required
def settings_view():
    return "Hello, World!"
