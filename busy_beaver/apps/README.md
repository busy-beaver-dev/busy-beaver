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

### GitHub Webhook

Events from the [busy-beaver-dev](https://github.com/busy-beaver-dev/busy-beaver)
organization are shared in the `#busy-beaver-meta` channel on
the Chicago Python slack.
This room is the hub of all Busy Beaver activities.

Currently we post messages when:

- an issue is created
- a Pull Request is opened

There are many other Slack integrations which
post messages when triggered by GithHub events.
We do not supporting webhooks for repositories that
are not part of `busy-beaver-dev`.
This might change in the future,
but for now there are other things to work on.

Note: In order to work on this feature,
you will need to set up a
[secret token](https://developer.github.com/webhooks/securing/#setting-your-secret-token)
on a GitHub repository.

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
