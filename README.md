# Busy Beaver

<p align="center"><img src="assets/logo.png" alt="Busy Beaver Logo" width=300 /></p>

[![Build Status](https://travis-ci.org/alysivji/busy-beaver.svg?branch=master)](https://travis-ci.org/alysivji/busy-beaver) [![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)](https://opensource.org/licenses/MIT)

Slack bot that summarizes public GitHub activity for registered users.

## Introduction

With over four thousand members, the [Chicago Python Users Group](https://www.chipy.org/) is one of the largest Python communities in the world. Slack has become the primary method of communication amongst our members in-between events. We decided to develop a Slack bot that summaries GitHub activity for registered users in a specific channel to increase member engagement. The goal is to spark conversations around tools and projects.

Users can sign up for an account by messaging the bot with a specific passphrase. The bot will request that the user sign into GitHub with a provided link. This process will ensure that only authorized GitHub activity is posted in the channel.

## Project Information

### Installation Notes

Create a Slack app via the [Slack API](https://api.slack.com/). The app will need **Event Subscriptions** configured to send information to a server for processing. Specifically, the Slack app is subscribed to [message.im](https://api.slack.com/events/message.im) bot events, which include direct messages sent to the bot. The app will also need scopes configured in **OAuth & Permissions** (see [here](#Slack-Permission-Scopes)).

Configure a server with an endpoint URL to receive HTTP POST requests when `message.im` events occur. A service like [ngrok](https://ngrok.com/) is useful here for local development purposes.

Create a GitHub app. The sole function of this app is to provide a means for the Slack user to validate their GitHub account.

When a Slack user chats "connect" to the bot user via direct message, the server receives the event details and generates a unique `state` identifier. The server logs the Slack user and identifier to our server database. The bot user chats a GitHub URL containing our GitHub app's `client_id` and the `state` identifier. The URL leads the user to a validation page in which they log in to GitHub and approve access to basic public information. Upon approval, the GitHub user's details and `state` identifier are sent to another server endpoint. The server updates the Slack user record with GitHub user details by using the `state` identifier as a common key.

### API Docs

- Kick off summary run by making a `POST` request to `/github-summary` with `Authentication` header set to `token {token}` and JSON body:

```json
{
  "channel": "channel_to_post"
}
```

### Stack

- [requests](https://github.com/requests/requests)
- [responder](https://github.com/kennethreitz/responder)
- [sqlalchemy](https://www.sqlalchemy.org/)

### Tests

- [pytest](https://github.com/pytest-dev/pytest)
- [vcr.py](https://github.com/kevin1024/vcrpy)
- [pytest-vcr](https://github.com/ktosiek/pytest-vcr)

`vcr.py` records cassettes of requests and responses for new tests, and replays them for previously written tests. Make sure to [filter credentials](https://vcrpy.readthedocs.io/en/latest/advanced.html#filter-information-from-http-headers)

## Development Environment

```console
export DATABASE_URI=sqlite:///busy_beaver.db

export GITHUB_APP_CLIENT_ID=[client-id]
export GITHUB_APP_CLIENT_SECRET=[client-secret]
export GITHUB_OAUTH_TOKEN=[token-here]

export SLACK_BOTUSER_OAUTH_TOKEN=[token-here]
```

Leverage Docker-Compose to create a containerized local development environment. Please see the `Makefile` for available commands.

### [pdb++](https://pypi.org/project/pdbpp/) Configuration

```python
# ./.pdbrc.py

import pdb


class Config(pdb.DefaultConfig):
    sticky_by_default = True  # start in sticky mode
    current_line_color = 40  # black

    # Presentation
    # current_line_color = 47  # grey
```

## Deployment

```console
export DATABASE_URI=[database-uri]
export BUSY_BEAVER_API_TOKEN=[bb-api-token]

export GITHUB_APP_CLIENT_ID=[client-id]
export GITHUB_APP_CLIENT_SECRET=[client-secret]
export GITHUB_OAUTH_TOKEN=[token-here]

export SLACK_BOTUSER_OAUTH_TOKEN=[token-here]

export SENTRY_DSN=[sentry-dsn]
export DATADOG_API_KEY=[datadog-api-key]
```

- [Travis CI](https://travis-ci.org/alysivji/busy-beaver) kicks off build of the deployment docker image when `master` has new commits.
- Image is uploaded to [DockerHub](https://cloud.docker.com/u/alysivji/repository/docker/alysivji/busy-beaver)
- [watchtower](https://github.com/v2tec/watchtower) monitors DockerHub and deploys latest image

### Creating Account for API

```python
admin = ApiUser(username="admin", token="abc123!")
db.session.add(admin)
db.session.commit()
```

---

## Slack Permission Scopes

```text
CONVERSATIONS
Access information about user’s public channels
channels:read

Send messages as BusyBeaverStaging
chat:write:bot

INTERACTIVITY
Add a bot user with the username @busybeaver
bot

BOT EVENTS
A message was posted in a direct message channel
message.im
```

---

## Long Horizon Todo

- [ ] ETag, need to set up DB for this
  - [ ] mark events that are new
- [ ] [rate limiting](https://developer.github.com/v3/#rate-limiting)
- [ ] [GraphQL](https://developer.github.com/v4/)

### GitHub Events

- [x] [CreateEvent](https://developer.github.com/v3/activity/events/types/#createevent) `ref_type` repository
- [x] [ForkEvent](https://developer.github.com/v3/activity/events/types/#forkevent)
- [x] [IssuesEvent](https://developer.github.com/v3/activity/events/types/#issuesevent) `action` opened
- [x] [PublicEvent](https://developer.github.com/v3/activity/events/types/#publicevent)
- [x] [PullRequestEvent](https://developer.github.com/v3/activity/events/types/#pullrequestevent) `action` opened
- [x] [PushEvent](https://developer.github.com/v3/activity/events/types/#pushevent)
- [x] [ReleaseEvent](https://developer.github.com/v3/activity/events/types/#releaseevent)
- [x] [WatchEvent](https://developer.github.com/v3/activity/events/types/#watchevent) `action` started

- [ ] [PullRequestReviewEvent](https://developer.github.com/v3/activity/events/types/#pullrequestreviewevent) `action` submitted **maybe**
- [ ] [RepositoryEvent](https://developer.github.com/v3/activity/events/types/#repositoryevent) (not a timeline event)
