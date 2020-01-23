# GitHub Integration

GitHub-related integration code GitHub

## Background

Leverages

- [GitHub OAuth](https://developer.github.com/apps/building-oauth-apps/authorizing-oauth-apps/)
- [GitHub Webhooks](https://developer.github.com/webhooks/)
- GitHub JSON API to generate a GitHub summary

## Features

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
