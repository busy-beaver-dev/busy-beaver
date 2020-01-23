# Applications

Each package inside of this folder contains Busy Beaver features.

## Features

### Events Database

This feature polls Meetup once a day and
adds syncs database with fetched events.

- new event get created
- removed events get deleted
- existing events get updated

### GitHub Summary

Public GitHub activity of registered users is shared
on a Slack channel once a day.

### GitHub Webhook

Events from the [busy-beaver-dev](https://github.com/busy-beaver-dev)
organization are shared in the `#busy-beaver-meta` channel on
the Chicago Python slack.
This room is the hub of all Busy Beaver activities.

Currently we post messages when:

- an issue is created
- a Pull Request is opened
- a new release is published

There are many other Slack integrations which
post messages when triggered by GithHub events.
We do not support GitHub webhooks for repositories that
are not part of `busy-beaver-dev` organization.
This might change in the future,
but for now there are other things to work on.

Note: In order to work on this feature,
you will need to set up a
[secret token](https://developer.github.com/webhooks/securing/#setting-your-secret-token)
in a GitHub repository.

### OAuth Integrations

Contains logic for integration with third-party APIs.
We provide a nice wrapper around `requests-oauthlib`
to simplify the OAuth process for the user.

### Retweeter

This feature shares tweets made by a given Twitter account
in a Slack workspace after a configurable length of time has passed.

### Slack Integration

Contains actual business logic for handling Slack Slash Commands and Slack Event Callbacks.

Users can use the following commands:

- `/busybeaver connect` to create a new account,
- `/busybeaver reconnect` to link Slack ID to different GitHub account
- `/busybeaver disconnect` to delete user account.

### Upcoming Events

TODO -- merge this app with the Slack Integration

- Users can query the database using the
[Slack slash commands](https://api.slack.com/slash-commands)
  - `/busybeaver next`
  - `/busybeaver events`
- The contents of `/busybeaver events` will be posted a specified channel
when an endpoint gets hit with a POST request;
this is currently triggered with a CRON job
