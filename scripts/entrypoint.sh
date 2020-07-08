#!/bin/bash
# Set strict mode options
set -euo pipefail

# Set default value for the server
DEFAULT="webserver"
SERVER=${1:-$DEFAULT}

# Set a default value for production status
PRODUCTION=${IN_PRODUCTION:-0}

if [ "$SERVER" = "webserver" ]; then
    echo "Starting Flask server"
    if [ "$PRODUCTION" = 1 ]; then
        gunicorn "busy_beaver:create_app()" -b 0.0.0.0:5000
    elif [ "$PRODUCTION" = 0 ]; then
        gunicorn "busy_beaver:create_app()" -b 0.0.0.0:5000 --reload --timeout 100000
    else
        echo "Unrecognized option for variable IN_PRODUCTION: '$PRODUCTION'"
        exit 1
    fi
elif [ "$SERVER" = "worker" ]; then
    echo "Starting RQ worker"
    python scripts/start_async_worker.py
elif [ "$SERVER" = "scheduler" ]; then
    echo "Starting RQ scehduler"
    python scripts/start_rq_scheduler.py
else
    echo "Unrecognized option for server: '$SERVER'"
    exit 1
fi
