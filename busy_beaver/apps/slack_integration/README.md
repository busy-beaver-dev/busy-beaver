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

## Installing in Slack Workspace

Distrbituion URL:

https://slack.com/oauth/v2/authorize?client_id=795376369155.506256439575&scope=app_mentions:read,channels:history,channels:join,channels:read,chat:write,commands,emoji:read,groups:read,im:history,im:read,im:write,mpim:history,mpim:read,mpim:write,reactions:read,reactions:write,team:read,usergroups:read,users.profile:read,users:read,users:write&user_scope=channels:read,groups:read
