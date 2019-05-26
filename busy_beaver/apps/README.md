# Applications

Each package inside of this folder contains Busy Beaver features.

## Events Database

This feature polls Meetup once a day and
adds new events to the application's database.

## GitHub Summary

Public GitHub activity of registered users is shared
on a Slack channel once a day.
Users can use the following commands:
`/busybeaver connect` to create a new account,
`/busybeaver reconnect` to link Slack ID to different GitHub account,
and `/busybeaver disconnect` to delete user account.

## Retweeter

This feature shares tweets made by a given Twitter account
in a Slack workspace after a configurable length of time has passed.

## Upcoming Events

Users can use the Slash commands `/busybeaver next` and `/busybeaver events`
to query the Meetup API for coming events.
