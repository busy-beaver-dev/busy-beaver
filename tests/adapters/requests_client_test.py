from busy_beaver.adapters.requests_client import RequestsClient


def test_adding_headers():
    requests = RequestsClient(headers={"Accept": "application/json/test"})
    assert requests.headers["Accept"] == "application/json/test"


def test_add_header_after_initailizing_without_headers():
    requests_client_no_header = RequestsClient()
    requests = RequestsClient(headers={"Accept": "application/json/test"})

    assert len(requests.headers) >= len(requests_client_no_header.headers)
