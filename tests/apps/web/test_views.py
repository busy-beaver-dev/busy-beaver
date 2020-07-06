def test_index(client):
    rv = client.get("/")
    assert rv.status_code == 200


def test_access_restricted_view(client):
    rv = client.get("/settings", follow_redirects=True)
    assert rv.status_code == 200
    assert "slack.com/oauth/v2/authorize" in rv.data.decode("utf-8")


def test_login_and_access_restricted_view(login_client, factory):
    slack_user = factory.SlackUser()
    client = login_client(user=slack_user)

    rv = client.get("/settings", follow_redirects=True)
    assert rv.status_code == 200
