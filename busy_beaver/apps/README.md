# Applications

Each package inside of this folder contains Busy Beaver features.

## Features

### Events Database

This feature polls Meetup once a day and
adds new events to the application's database.

### GitHub Summary

Public GitHub activity of registered users is shared
on a Slack channel once a day.

Users can use the following commands:

- `/busybeaver connect` to create a new account,
- `/busybeaver reconnect` to link Slack ID to different GitHub account
- `/busybeaver disconnect` to delete user account.

### Retweeter

This feature shares tweets made by a given Twitter account
in a Slack workspace after a configurable length of time has passed.

### Upcoming Events

- Users can query the database using the [Slack slash commands](https://api.slack.com/slash-commands)
  - `/busybeaver next`
  - `/busybeaver events`
- The contents of `/busybeaver events` will be posted a specified channel
when an endpoint gets hit with a POST request;
this is currently triggered with a CRON job
