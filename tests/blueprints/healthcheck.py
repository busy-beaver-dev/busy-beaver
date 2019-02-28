def test_healthcheck(client):
    rv = client.get("/api/healthcheck")
    assert rv.status_code == 200
    assert rv.json is True
