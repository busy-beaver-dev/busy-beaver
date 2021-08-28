from datetime import timedelta
import logging
import random
from typing import List, NamedTuple

from sqlalchemy import and_

from .blocks import GitHubSummaryPost
from .summary import GitHubUserEvents
from busy_beaver.clients import github_async
from busy_beaver.common.wrappers import SlackClient
from busy_beaver.exceptions import ValidationError
from busy_beaver.extensions import rq
from busy_beaver.models import GitHubSummaryUser, SlackInstallation
from busy_beaver.toolbox import generate_range_utc_now_minus, set_task_progress

logger = logging.getLogger(__name__)


class UserEvents(NamedTuple):
    user: GitHubSummaryUser
    events: GitHubUserEvents


@rq.job
def post_github_summary_message(workspace_id: str):
    installation = SlackInstallation.query.filter_by(workspace_id=workspace_id).first()
    if not installation:
        raise ValidationError("workspace not found")

    start_dt, end_dt = generate_range_utc_now_minus(timedelta(days=1))
    fetch_github_summary_post_to_slack(installation, start_dt, end_dt)
    set_task_progress(100)


def fetch_github_summary_post_to_slack(installation, start_dt, end_dt):
    channel = installation.github_summary_config.channel
    slack = SlackClient(installation.bot_access_token)

    # Step 1: find active users
    channel_members = slack.get_channel_members(channel)
    users: List[GitHubSummaryUser] = GitHubSummaryUser.query.filter(
        and_(
            GitHubSummaryUser.config_id == installation.github_summary_config.id,
            GitHubSummaryUser.slack_id.in_(channel_members),
            GitHubSummaryUser.github_username.isnot(None),
        )
    ).all()
    random.shuffle(users)

    # Step 2: get GitHub activity for users
    users_by_github_username = {user.github_username: user for user in users}
    usernames = users_by_github_username.keys()
    activity_by_user = github_async.get_activity_for_users(usernames, start_dt, end_dt)

    # Step 3: classify activity by event type
    all_user_events = []
    for _, user in enumerate(users):
        user_activity = activity_by_user[user.github_username]

        logger.info("Compiling stats for {0}".format(user))
        if len(user_activity) == 0:
            continue

        user_events = GitHubUserEvents.classify_events_by_type(user, user_activity)
        all_user_events.append(UserEvents(user, user_events))

    # Step 4: format message and post to Slack
    github_summary_post = GitHubSummaryPost(all_user_events)
    slack.post_message(
        blocks=github_summary_post.as_blocks(),
        channel=channel,
        unfurl_links=False,
        unfurl_media=False,
    )
