#!/bin/bash

source ${HOME}/.bash_profile

docker-compose \
    -f ${HOME}/busy-beaver/docker-compose.prod.yml \
    exec db pg_dump -U ${POSTGRES_USER} busy-beaver > /tmp/data_dump.sql

docker run --rm -t \
    -v ${HOME}/.aws:/home/worker/.aws:ro \
    -v ${HOME}/busy-beaver/scripts/prod/backup-db:/work \
    -v /tmp/data_dump.sql:/tmp/data_dump.sql \
    shinofara/docker-boto3 python /work/upload_db_backup_to_s3.py
