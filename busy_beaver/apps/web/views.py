import logging

from flask import jsonify, redirect, render_template, url_for
from flask.views import View
from flask_login import current_user, login_required, logout_user

from .blueprint import web_bp
from .forms import (
    AddNewGroupConfigurationForm,
    GitHubSummaryConfigurationForm,
    UpcomingEventsConfigurationForm,
)
from busy_beaver.apps.slack_integration.oauth.workflow import (
    create_or_update_configuration,
)
from busy_beaver.apps.upcoming_events.workflow import (
    add_new_group_to_configuration,
    create_or_update_upcoming_events_configuration,
)
from busy_beaver.common.wrappers import SlackClient
from busy_beaver.exceptions import NotAuthorized
from busy_beaver.extensions import db
from busy_beaver.models import UpcomingEventsGroup

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
    slack = SlackClient(installation.bot_access_token)

    is_admin = slack.is_admin(current_user.slack_id)
    if not is_admin:
        raise NotAuthorized("Need to be an admin to access")

    form = GitHubSummaryConfigurationForm()
    form.channel.choices = slack.get_bot_channels()
    if form.validate_on_submit():
        logger.info("Attempt to save GitHub Summary settings")
        create_or_update_configuration(
            installation,
            channel=form.data["channel"],
            summary_post_time=form.data["summary_post_time"],
            summary_post_timezone=form.data["summary_post_timezone"],
            slack_id=current_user.slack_id,
        )
        logger.info("GitHub Summary settings changed successfully")
        return jsonify({"message": "Settings changed successfully"})

    # load default
    try:
        config = installation.github_summary_config
        form.summary_post_time.data = config.summary_post_time
        form.summary_post_timezone.data = config.summary_post_timezone.zone
        form.channel.data = config.channel
        enabled = config.enabled
    except AttributeError:
        enabled = False

    return render_template("github_summary_settings.html", form=form, enabled=enabled)


@web_bp.route("/settings/github-summary/toggle")
@login_required
def toggle_github_summary_config_view():
    logger.info("Toggling Github Summary enabled state")
    installation = current_user.installation
    slack = SlackClient(installation.bot_access_token)

    is_admin = slack.is_admin(current_user.slack_id)
    if not is_admin:
        raise NotAuthorized("Need to be an admin to access")

    config = installation.github_summary_config
    if not config:
        return jsonify({"error": "Need to enter post time and timezone"})
    config.toggle_configuration_enabled_status()
    db.session.add(config)
    db.session.commit()
    return redirect(url_for("web.github_summary_settings"))


@web_bp.route("/settings/upcoming-events", methods=("GET", "POST"))
@login_required
def upcoming_events_settings():
    logger.info("Hit Upcoming Events Settings page")
    installation = current_user.installation
    config = installation.upcoming_events_config
    slack = SlackClient(installation.bot_access_token)

    is_admin = slack.is_admin(current_user.slack_id)
    if not is_admin:
        raise NotAuthorized("Need to be an admin to access")

    form = UpcomingEventsConfigurationForm()
    form.channel.choices = slack.get_bot_channels()
    if form.validate_on_submit():
        logger.info("Attempt to save Upcoming Events settings")
        create_or_update_upcoming_events_configuration(
            installation,
            channel=form.data["channel"],
            post_day_of_week=form.data["post_day_of_week"],
            post_time=form.data["post_time"],
            post_timezone=form.data["post_timezone"],
            post_num_events=form.data["post_num_events"],
            slack_id=current_user.slack_id,
        )
        logger.info("Upcoming Events settings changed successfully")
        return jsonify({"message": "Settings changed successfully"})

    # load default
    try:
        form.channel.data = config.channel
        form.post_day_of_week.data = config.post_day_of_week
        form.post_time.data = config.post_time
        form.post_timezone.data = config.post_timezone.zone
        form.post_num_events.data = config.post_num_events
        groups = [group.meetup_urlname for group in config.groups]
        enabled = config.enabled
    except AttributeError:
        enabled = False
        groups = []

    return render_template(
        "upcoming_events_settings.html", form=form, enabled=enabled, groups=groups
    )


@web_bp.route("/settings/upcoming-events/toggle")
@login_required
def toggle_upcoming_events_config_view():
    logger.info("Toggling Upcoming Events enabled state")
    installation = current_user.installation
    slack = SlackClient(installation.bot_access_token)

    is_admin = slack.is_admin(current_user.slack_id)
    if not is_admin:
        raise NotAuthorized("Need to be an admin to access")

    config = installation.upcoming_events_config
    if not config:
        return jsonify({"error": "Need to enter post time and timezone"})
    config.toggle_configuration_enabled_status()
    db.session.add(config)
    db.session.commit()
    return redirect(url_for("web.upcoming_events_settings"))


@web_bp.route("/settings/upcoming-events/group", methods=("GET", "POST"))
@login_required
def upcoming_events_add_new_group():
    logger.info("Hit Upcoming Events Settings -- Add New Group page")
    installation = current_user.installation
    config = installation.upcoming_events_config
    slack = SlackClient(installation.bot_access_token)

    is_admin = slack.is_admin(current_user.slack_id)
    if not is_admin:
        raise NotAuthorized("Need to be an admin to access")

    form = AddNewGroupConfigurationForm()
    if form.validate_on_submit():
        logger.info("Attempt to add new group")
        add_new_group_to_configuration(
            config, meetup_urlname=form.data["meetup_urlname"]
        )
        logger.info("New group added")
        return jsonify({"message": "Group added successfully"})

    # load default
    try:
        groups = config.groups
    except AttributeError:
        groups = []

    return render_template(
        "upcoming_events_add_new_group.html", form=form, groups=groups
    )


# TODO this is making a GET call
@web_bp.route("/settings/upcoming-events/group/<int:id>/delete")
@login_required
def upcoming_events_delete_group(id):
    logger.info("Hit Upcoming Events Settings -- Remove group view")
    installation = current_user.installation
    slack = SlackClient(installation.bot_access_token)

    is_admin = slack.is_admin(current_user.slack_id)
    if not is_admin:
        raise NotAuthorized("Need to be an admin to access")

    matching_group = UpcomingEventsGroup.query.get_or_404(id)
    db.session.delete(matching_group)
    db.session.commit()
    return redirect(url_for("web.upcoming_events_add_new_group"))
