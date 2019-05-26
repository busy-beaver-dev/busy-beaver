def test_healthcheck(client):
    rv = client.get("/healthcheck")
    assert rv.status_code == 200
