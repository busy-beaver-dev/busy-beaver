import uuid

import boto3

from busy_beaver.config import (
    DIGITALOCEAN_SPACES_BASE_URL,
    DIGITALOCEAN_SPACES_ENDPOINT_URL,
    DIGITALOCEAN_SPACES_REGION_NAME,
)

# TODO make this folder change depending on dev, staging and production
LOGO_FOLDER = "bb-logos"


# TODO test this using LocalStack
# test is to upload a file and then check to see if you can download
# should be the same bytes
# TODO rename this to BlobStorageClient
class S3Client:
    def __init__(self, client_key, client_secret):
        session = boto3.session.Session()
        self.client = session.client(
            "s3",
            region_name=DIGITALOCEAN_SPACES_REGION_NAME,
            endpoint_url=DIGITALOCEAN_SPACES_ENDPOINT_URL,
            aws_access_key_id=client_key,
            aws_secret_access_key=client_secret,
        )

    def upload_logo(self, filelike_object):
        extension = filelike_object.filename.split(".")[-1]
        filepath = f"{LOGO_FOLDER}/{str(uuid.uuid4())}.{extension}"

        response = self.client.put_object(
            Bucket="sivdn", Body=filelike_object, ACL="public-read", Key=filepath
        )

        status_code = response["ResponseMetadata"]["HTTPStatusCode"]
        if status_code != 200:
            raise Exception(
                "Raise a FormValidation error; or maybe a different error to let me "
                "know something went wrong and try again"
            )

        url = self._generate_url(filepath)
        return url

    def _generate_url(self, filepath):
        return f"{DIGITALOCEAN_SPACES_BASE_URL}/{filepath}"
