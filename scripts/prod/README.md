# Production Scripts

## `run_github_summary_report.sh`

### CRON Settings

0 19 * * * /bin/bash /home/alysivji/busy-beaver/scripts/prod/run_github_summary_report.sh

## Lambda Function

`Under construction`

```python
import json
from botocore.vendored import requests

CHANNEL_ID = ""
CHANNEL_NAME = "busy-beaver"
TOKEN = ""


def lambda_handler(event, context):
    url = "https://busybeaver.sivji.com/github-summary"
    headers = {"Authorization": f"token {TOKEN}"}
    payload = {"channel": CHANNEL_ID}

    return requests.post(url, headers=headers, data=json.dumps(payload))
```
