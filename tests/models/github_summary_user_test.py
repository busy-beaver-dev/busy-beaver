import pytest

from busy_beaver.models import GitHubSummaryUser, SlackInstallation


@pytest.mark.wip
def test_github_summary_user_to_slack_relationship(session):
    installation = SlackInstallation(
        access_token="abc",
        authorizing_user_id="def",
        bot_access_token="ghi",
        bot_user_id="jkl",
        scope="test_scope",
        workspace_id="123",
        workspace_name="456",
    )

    user = GitHubSummaryUser(
        slack_id="123",
        github_id="abc",
        github_username="def",
        github_state="ghi",
        github_access_token="jkl",
    )
    user.installation = installation

    # Act
    session.add(installation)
    session.add(user)
    session.commit()

    # Assert
    user_in_db = GitHubSummaryUser.query.first()
    assert user_in_db.installation == installation

    installation_in_db = SlackInstallation.query.first()
    assert user in installation_in_db.github_summary_users
