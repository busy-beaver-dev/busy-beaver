def test_index(client):
    rv = client.get("/")
    assert rv.status_code == 200
