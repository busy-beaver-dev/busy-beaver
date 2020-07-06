import logging

from flask import redirect, render_template, url_for
from flask.views import View
from flask_login import current_user, login_required, logout_user

from .blueprint import web_bp
from busy_beaver.common.wrappers import SlackClient

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
web_bp.add_url_rule(
    "/login", view_func=RenderTemplateView.as_view("login", template_name="login.html")
)


@web_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("web.home"))


@web_bp.route("/settings")
@login_required
def settings_view():
    installation = current_user.installation
    slack = SlackClient(installation.bot_access_token)

    is_admin = slack.is_admin(current_user.slack_id)
    template_context = {"is_admin": is_admin}

    return render_template("settings.html", **template_context)
