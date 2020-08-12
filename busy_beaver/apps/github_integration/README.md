# GitHub Integration

GitHub-related integration code GitHub

## Background

Leverages

- [GitHub OAuth](https://developer.github.com/apps/building-oauth-apps/authorizing-oauth-apps/)
- [GitHub Webhooks](https://developer.github.com/webhooks/)
- GitHub JSON API to generate a GitHub summary

## Features

### GitHub OAuth

Our GitHub OAuth application allows us to connect Slack users to their GitHub IDs.

> User can trigger login using `/busybeaver connect`, the server receives the event details and generates a unique `state` identifier. The server logs the Slack user and identifier to our server database. The bot user sends a message to the user with a GitHub URL containing our GitHub app's `client_id` and the `state` identifier. The URL leads the user to a validation page in which they log in to GitHub and approve access to basic public information. Upon approval, the GitHub user's details and `state` identifier are sent to another server endpoint. The server updates the Slack user record with GitHub user details by using the `state` identifier as a common key.

#### Todo

- what if user disconencts the app from GitHub? We should try out the token everytime to confirm and delete...

### GitHub Summary

Public GitHub activity of registered users is shared
on a Slack channel once a day.

Busy Beaver currently supports the following GitHub public events:

- [CreateEvent](https://developer.github.com/v3/activity/events/types/#createevent) `ref_type` repository
- [ForkEvent](https://developer.github.com/v3/activity/events/types/#forkevent)
- [IssuesEvent](https://developer.github.com/v3/activity/events/types/#issuesevent) `action` opened
- [PublicEvent](https://developer.github.com/v3/activity/events/types/#publicevent)
- [PullRequestEvent](https://developer.github.com/v3/activity/events/types/#pullrequestevent) `action` opened
- [PushEvent](https://developer.github.com/v3/activity/events/types/#pushevent)
- [ReleaseEvent](https://developer.github.com/v3/activity/events/types/#releaseevent)
- [WatchEvent](https://developer.github.com/v3/activity/events/types/#watchevent) `action` started

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
