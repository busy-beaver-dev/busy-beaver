import logging

from flask import jsonify, redirect, render_template, url_for
from flask.views import View
from flask_login import current_user, login_required, logout_user

from .blueprint import web_bp
from .forms import GitHubSummaryConfigurationForm
from busy_beaver.common.wrappers import SlackClient
from busy_beaver.exceptions import NotAuthorized
from busy_beaver.extensions import db

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


class RenderTemplateLoginRequiredView(RenderTemplateView):

    decorators = [login_required]


web_bp.add_url_rule(
    "/settings",
    view_func=RenderTemplateLoginRequiredView.as_view(
        "settings_view", template_name="settings.html"
    ),
)


@web_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("web.home"))


@web_bp.route("/settings/github-summary", methods=("GET", "POST"))
@login_required
def github_summary_settings():
    logger.info("Hit GitHub Summary Settings page")
    installation = current_user.installation
    config = installation.github_summary_config
    slack = SlackClient(installation.bot_access_token)

    is_admin = slack.is_admin(current_user.slack_id)
    if not is_admin:
        raise NotAuthorized("Need to be an admin to access")

    form = GitHubSummaryConfigurationForm()
    if form.validate_on_submit():
        logger.info("Trying to change config settings")
        config.summary_post_time = form.data["summary_post_time"]
        config.summary_post_timezone = form.data["summary_post_timezone"]
        db.session.add(config)
        db.session.commit()

        logger.info("Changed successfully")
        return jsonify({"message": "Settings changed successfully"})

    # load default
    form.summary_post_time.data = config.summary_post_time
    form.summary_post_timezone.data = config.summary_post_timezone.zone

    channel = config.channel
    channel_info = slack.channel_details(channel)
    return render_template("set_time.html", form=form, channel=channel_info["name"])
