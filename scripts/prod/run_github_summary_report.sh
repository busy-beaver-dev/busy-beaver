#!/bin/bash

source $HOME/.bash_profile

curl https://busybeaver.sivji.com/poll/github-summary \
    -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: token ${BUSY_BEAVER_API_TOKEN}" \
    -d '{"workspace_id": "T093FC1RC", "channel": "busy-beaver"}'
