#!/bin/bash

source $HOME/.bash_profile

curl https://busybeaver.sivji.com/poll/upcoming-events \
    -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: token ${BUSY_BEAVER_API_TOKEN}" \
    -d '{"channel": "announcements"}'
