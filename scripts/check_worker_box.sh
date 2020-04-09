#!/bin/bash

# Check to see if worker box is still active
# Used for Kubernetes probes
rq info -u ${REDIS_URI} --only-workers | grep -q ${HOSTNAME}
