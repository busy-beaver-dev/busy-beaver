#!/bin/bash

if [ "$1" = "webserver" ]; then
    echo "Starting Flask server"
    flask db upgrade
    if [ "$IN_PRODUCTION" = 1 ]; then
        gunicorn "busy_beaver:create_app()" -b 0.0.0.0:5000
    else
        gunicorn "busy_beaver:create_app()" -b 0.0.0.0:5000 --reload --timeout 100000
    fi
elif [ "$1" = "worker" ]; then
    echo "Starting RQ worker"
    python start_async_worker.py
else
    exit 1
fi
