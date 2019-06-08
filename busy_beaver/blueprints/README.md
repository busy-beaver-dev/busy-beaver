# Flask Blueprints

All web framework specific code is located in this directory.
Levarege [Flask Blueprints pattern](http://flask.pocoo.org/docs/1.0/blueprints/)
quite extensively.

## GitHub

Contains logic to integrate
[GitHub Webhooks](https://developer.github.com/webhooks/).
Also contains
[GitHub OAuth](https://developer.github.com/apps/building-oauth-apps/authorizing-oauth-apps/)
logic.

## Poller

This folder contains all endpoints that are used to trigger tasks.
The tasks are in the `apps` folder

The current workflow we have for periodic tasks:

- run GitHub Summary
- run job to post new tweets to Twitter
- run task to update Events database with new events from meetup
- run workflow to post upcoming events to a Slack channel

## Slack

Contains logic to integrate Slack webhooks.

We are currently using

- [Event Subscription API](https://api.slack.com/events-api)
- [Slash Commands](https://api.slack.com/slash-commands)
  - commands are dispatched to the command handlers using `EventEmitter`
