# Applications

Each package inside of this folder contains Busy Beaver features.
All web framework specific code is located in this directory.
Levarege [Flask Blueprints pattern](http://flask.pocoo.org/docs/1.0/blueprints/)
quite extensively.

All web framework specific code is located in this directory.
Levarege [Flask Blueprints pattern](http://flask.pocoo.org/docs/1.0/blueprints/)
quite extensively.
Flask code is in `api` subfolders

## Features

### Events Database

This feature polls Meetup once a day and
adds syncs database with fetched events.

- new event get created
- removed events get deleted
- existing events get updated

### GitHub Integration

GitHub-related integration code GitHub

## Poller

Endpoints that are used to trigger tasks.
Should really make these CRON jobs.

The current workflow we have for periodic tasks:

- run GitHub Summary
- run job to post new tweets to Twitter
- run task to update Events database with new events from meetup
- run workflow to post upcoming events to a Slack channel

### Retweeter

This feature shares tweets made by a given Twitter account
in a Slack workspace after a configurable length of time has passed.

### Slack Integration

All code related to integrating with Slack.
We are currently using:

- [Event Subscription API](https://api.slack.com/events-api)
- [Slash Commands](https://api.slack.com/slash-commands)
  - commands are dispatched to the command handlers using `EventEmitter`

#### Commands

Users can use the following commands:

- `/busybeaver connect` to create a new account,
- `/busybeaver reconnect` to link Slack ID to different GitHub account
- `/busybeaver disconnect` to delete user account.

TODO update this

### Upcoming Events

TODO -- merge this app with the Slack Integration

- Users can query the database using the
[Slack slash commands](https://api.slack.com/slash-commands)
  - `/busybeaver next`
  - `/busybeaver events`
- The contents of `/busybeaver events` will be posted a specified channel
when an endpoint gets hit with a POST request;
this is currently triggered with a CRON job
