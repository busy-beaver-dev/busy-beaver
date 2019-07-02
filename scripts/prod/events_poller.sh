#!/bin/bash

source $HOME/.bash_profile

curl https://busybeaver.sivji.com/poll/sync-event-database \
    -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: token ${BUSY_BEAVER_API_TOKEN}"
