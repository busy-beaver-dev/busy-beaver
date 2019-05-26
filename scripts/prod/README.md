# Busy Beaver Production Scripts

## Contents

### `run_github_summary_report.sh`

Script that posts daily Summary Reports on Slack. This script is configured to run via a CRON job at 19:00 UTC everyday. CRON job has been documented in ansible configuration.

### `twitter_poller.sh`

Script that polls `@ChicagoPython` on Twitter to find tweets to publish to Slack. Posts tweets one at a time.

### `backup-db`

Script that runs `pg_dump` and uploads resulting `.sql` file to S3.

### `events_poller.sh`

Script that polls `_ChiPy_` on Meetup to find new events that can be added to the database. Runs once a day.
