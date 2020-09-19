import io
import uuid

import pytest
import requests

from busy_beaver.config import (
    DIGITALOCEAN_SPACES_BASE_URL,
    DIGITALOCEAN_SPACES_ENDPOINT_URL,
)


@pytest.mark.unit
def test_find_bucket_that_does_not_exist(s3):
    random_bucket = str(uuid.uuid4())
    assert s3.find_bucket(random_bucket) is False


@pytest.mark.unit
def test_create_bucket_and_then_delete_it(s3):
    random_bucket = str(uuid.uuid4())
    assert s3.create_bucket(random_bucket) is True
    assert s3.delete_bucket(random_bucket) is True


@pytest.mark.unit
def test_upload_logo_to_blob_store(s3):
    # Arrange
    logo_bytes = b"abcdefghijklmnopqrstuvwxyz"
    logo_file = io.BytesIO(logo_bytes)
    logo_file.filename = "testfile.txt"

    # Act
    url = s3.upload_logo(logo_file)

    # Assert -- fetch file to make sure it is what we expect
    modified_url = url.replace(
        DIGITALOCEAN_SPACES_BASE_URL, DIGITALOCEAN_SPACES_ENDPOINT_URL
    )
    resp = requests.get(modified_url)
    assert resp.text == logo_bytes.decode("utf-8")

    # TODO should we clean up?
    # it's in a container; not really worried about it at this stage
