import pytest


@pytest.mark.unit
def test_index(client):
    rv = client.get("/")
    assert rv.status_code == 200


class TestAuthentication:
    @pytest.mark.unit
    def test_access_restricted_view(self, client):
        rv = client.get("/settings", follow_redirects=True)
        assert rv.status_code == 200
        assert "slack.com/oauth/v2/authorize" in rv.data.decode("utf-8")

    @pytest.mark.unit
    def test_login_and_access_restricted_view(self, login_client, factory):
        slack_user = factory.SlackUser()
        client = login_client(user=slack_user)

        rv = client.get("/settings", follow_redirects=True)
        assert rv.status_code == 200

    @pytest.mark.unit
    def test_logout_view(self, login_client, factory):
        # Arrange
        slack_user = factory.SlackUser()
        client = login_client(user=slack_user)
        client.get("/logout", follow_redirects=True)

        # Act
        rv = client.get("/settings", follow_redirects=True)

        # Assert
        assert rv.status_code == 200
        assert "slack.com/oauth/v2/authorize" in rv.data.decode("utf-8")
