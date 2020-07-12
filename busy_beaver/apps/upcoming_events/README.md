# Upcoming Events

Display upcoming events from Meetup in Slack.

## Background

- Users can query the database using the
[Slack slash commands](https://api.slack.com/slash-commands)
  - `/busybeaver next`
  - `/busybeaver events`
- The contents of `/busybeaver events` will be posted a specified channel
when an endpoint gets hit with a POST request;
this is currently triggered with a CRON job

### Events Database

This feature polls Meetup once a day and
adds syncs database with fetched events.

- new event get created
- removed events get deleted
- existing events get updated
