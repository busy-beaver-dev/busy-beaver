# Poller

Endpoints that are used to trigger tasks.
Should really make these CRON jobs.

The current workflow we have for periodic tasks:

- run GitHub Summary
- run job to post new tweets to Twitter
- run task to update Events database with new events from meetup
- run workflow to post upcoming events to a Slack channel
