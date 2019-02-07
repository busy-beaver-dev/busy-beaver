# Busy Beaver

<p align="center"><img src="assets/logo.png" alt="Busy Beaver Logo" width=300 /></p>

[![Build Status](https://travis-ci.org/alysivji/busy-beaver.svg?branch=master)](https://travis-ci.org/alysivji/busy-beaver) [![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)](https://opensource.org/licenses/MIT)

Chicago Python's Community Engagement Slack bot.

## Introduction

With over four thousand members, the [Chicago Python Users Group](https://www.chipy.org/) (ChiPy) is one of the largest Python communities in the world. Slack has become the primary method of communication amongst our members in-between events. We developed an open-source Slack bot, codename: Busy Beaver, to increase community engagement.

[Slides from Busy Beaver's release announcement](http://bit.ly/busy-beaver). YouTube link is forthcoming.

## Features

### GitHub Activity

Busy-Beaver posts daily summaries of public GitHub activity for registered users in the `#busy-beaver` channel on the [ChiPy Slack](https://chipy.slack.com/). The goal of this feature is to increase engagement by sparking conversations around GitHub activity.

Users sign up for an account by `DM`ing the bot with the phrase: `connect`. The bot requires users to sign into GitHub to ensure only authorized activity is posted in the channel.

### Retweeter

Busy-Beaver retweets posts made to the [@ChicagoPython Twitter account](https://twitter.com/ChicagoPython) in the `#at-chicagopython` channel on the [ChiPy Slack](https://chipy.slack.com/).

### Roadmap

We are currently working on additional features to improve ChiPy community engagement. Please join the conversation in `#busy-beaver-meta` on the [ChiPy Slack](https://chipy.slack.com/).

## Development Notes

Busy-Beaver is an open source project where all artificats (code, Docker image, etc) are online. We use the [Twelve-Factor Application Methodology](https://12factor.net) for building services to design the CICD process and to keep information secure.

### Web Application Stack

- [sqlite](https://www.sqlite.org)
- [responder](https://github.com/kennethreitz/responder)
- [sqlalchemy](https://www.sqlalchemy.org/) with [sqla-wrapper](https://github.com/jpscaletti/sqla-wrapper)
- [requests](https://github.com/requests/requests)

### Tests

- [pytest](https://github.com/pytest-dev/pytest)
- [vcr.py](https://github.com/kevin1024/vcrpy)
- [pytest-vcr](https://github.com/ktosiek/pytest-vcr)
- [pytest-freezegun](https://github.com/ktosiek/pytest-freezegun)

`vcr.py` records cassettes of requests and responses for new tests, and replays them for previously written tests. Make sure to [filter credentials](https://vcrpy.readthedocs.io/en/latest/advanced.html#filter-information-from-http-headers)

### DevOps

- [watchtower](https://github.com/v2tec/watchtower) (monitors DockerHub, downloads and deploys latest image)
- [Ansible](https://www.ansible.com/)
- [DigitalOcean](https://www.digitalocean.com)

### Services

We are grateful to the following organizations for providing free services to open source projects:

- [GitHub](https://github.com) (code repo, issues)
- [DockerHub](https://hub.docker.com) (hosting Docker images)
- [Travis CI](https://travis-ci.org/) (continuous integration platform)

### Installation Notes

Create a Slack app via the [Slack API](https://api.slack.com/). The app will need **Event Subscriptions** configured to send information to a server for processing. Specifically, the Slack app is subscribed to [message.im](https://api.slack.com/events/message.im) bot events, which include direct messages sent to the bot. The app will also need scopes configured in **OAuth & Permissions** (see [here](#Slack-Permission-Scopes)).

Configure a server with an endpoint URL to receive HTTP POST requests when `message.im` events occur. A service like [ngrok](https://ngrok.com/) is useful here for local development purposes.

Create a GitHub app. The sole function of this app is to provide a means for the Slack user to validate their GitHub account.

When a Slack user chats "connect" to the bot user via direct message, the server receives the event details and generates a unique `state` identifier. The server logs the Slack user and identifier to our server database. The bot user chats a GitHub URL containing our GitHub app's `client_id` and the `state` identifier. The URL leads the user to a validation page in which they log in to GitHub and approve access to basic public information. Upon approval, the GitHub user's details and `state` identifier are sent to another server endpoint. The server updates the Slack user record with GitHub user details by using the `state` identifier as a common key.

### API Docs

Can make requests to REST endpoints to kick off processes. Currently we are using CRON to run repetitive tasks; [this is managed by Ansible](https://github.com/alysivji/busy-beaver/blob/master/ansible/roles/cron/tasks/main.yml) to avoid manual configuration.

#### GitHub Summary Endpoint

- Start the process to run a summary by making a `POST` request to `/poll-twitter` with `Authentication` header set to `token {token}` and JSON body:

```json
{
  "channel": "busy-beaver"
}
```

#### Retweeter Endpoint

- Check Twitter feed for new posts to share on Slack by making a `POST` request to `/github-summary` with `Authentication` header set to `token {token}` and JSON body:

```json
{
  "channel": "at-chicagopython"
}
```

#### Creating API Account and Token

```python
admin = ApiUser(username="admin", token="abc123!", role="admin")
db.session.add(admin)
db.session.commit()
```

## Development Environment

```console
export POSTGRES_USER=[username]
export POSTGRES_PASSWORD=[password]
export DATABASE_URI=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/busy-beaver

export GITHUB_APP_CLIENT_ID=[client-id]
export GITHUB_APP_CLIENT_SECRET=[client-secret]
export GITHUB_OAUTH_TOKEN=[token-here]

export SLACK_BOTUSER_OAUTH_TOKEN=[token-here]

export TWITTER_CONSUMER_KEY=[token-here]
export TWITTER_CONSUMER_SECRET=[token-here]
export TWITTER_ACCESS_TOKEN=[token-here]
export TWITTER_ACCESS_TOKEN_SECRET=[token-here]
```

Leverage Docker-Compose to create a containerized local development environment. Please see the `Makefile` for available commands.

### [pdb++](https://pypi.org/project/pdbpp/) Configuration

PDB++ improves the debugging experience inside the shell.

```python
# ./.pdbrc.py

import pdb


class Config(pdb.DefaultConfig):
    sticky_by_default = True  # start in sticky mode
    current_line_color = 40  # black
```

---

## Slack Permission Scopes

TODO: elaborate on permissions

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

## Todo

- [ ] ETag, need to set up DB for this
  - mark events that are new
- [ ] [rate limiting](https://developer.github.com/v3/#rate-limiting)
  - far away concern
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
