import pytest

from busy_beaver.common.wrappers import S3Client
from busy_beaver.config import (
    DIGITALOCEAN_SPACES_BUCKET_NAME,
    DIGITALOCEAN_SPACES_KEY,
    DIGITALOCEAN_SPACES_SECRET,
)

bucket = DIGITALOCEAN_SPACES_BUCKET_NAME


@pytest.fixture(scope="session")
def s3():
    """Create bucket for tests if it does not already exist"""
    s3 = S3Client(DIGITALOCEAN_SPACES_KEY, DIGITALOCEAN_SPACES_SECRET)

    created_bucket = False
    if not s3.find_bucket(bucket):
        s3.create_bucket(bucket)
        created_bucket = True

    yield s3

    if created_bucket:
        s3.delete_bucket(bucket)
