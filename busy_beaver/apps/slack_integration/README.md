# Slack Integration

All code related to integrating with Slack.
We are currently using:

- [Event Subscription API](https://api.slack.com/events-api)
- [Slash Commands](https://api.slack.com/slash-commands)
  - commands are dispatched to the command handlers using `EventEmitter`

## Commands

Users can use the following commands:

- `/busybeaver connect` to create a new account,
- `/busybeaver reconnect` to link Slack ID to different GitHub account
- `/busybeaver disconnect` to delete user account.

TODO update this
