#!/bin/bash

set +e

aws --endpoint-url=http://localhost:4566 --region us-east-1 s3api head-bucket --bucket ${BUCKET_NAME}

if [ $? -eq 0 ]
then
  exit 0
else
  echo "creating bucket"
  aws --endpoint-url=http://localhost:4566 --region us-east-1 \
    s3api create-bucket --bucket ${BUCKET_NAME} --acl public-read
  exit 0
fi
