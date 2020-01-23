# Applications

Each package inside of this folder contains Busy Beaver features.
All web framework specific code is located in this directory.
Levarege [Flask Blueprints pattern](http://flask.pocoo.org/docs/1.0/blueprints/)
quite extensively.
Flask code is in `api` subfolders.

## App Directory

|Application|Description
|---|---|
|debug|Tools to help development and debug|
|github_integration|GitHub related-integration logic|
|poller|Secure endpoints we use to trigger CRON jobs|
|retweeter|Shares tweets by a given Twitter account in Slack|
|slack_integration|Slack-related integration logic|
|upcoming_events|Display upcoming events from Meetup
