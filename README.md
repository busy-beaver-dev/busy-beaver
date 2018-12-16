# Busy Beaver

[![Build Status](https://travis-ci.org/alysivji/busy-beaver.svg?branch=master)](https://travis-ci.org/alysivji/busy-beaver)

Slack bot that posts GitHub activity summaries for registered users.

## Introduction

With over four thousand members, the [Chicago Python Users Group](https://www.chipy.org/) is one of the largest Python communities in the world. Slack has become the primary method of communication amongst our members in-between events. We decided to develop a Slack bot that summaries GitHub activity for registered users in a specific channel to increase member engagement. The goal is to spark conversations around tools and projects.

Users can sign up for an account by messaging the bot with a specific passphrase. The bot will request that the user sign into GitHub with a provided link. This process will ensure that only authorized GitHub activity is posted in the channel.

## Project Information

### Stack

- [requests](https://github.com/requests/requests)
- [responder](https://github.com/kennethreitz/responder)
- [sqlalchemy](https://www.sqlalchemy.org/)

### Workflow Diagram

- TODO

#### Tests

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

## Deployment

```console
export DATABASE_URI=[database-uri]

export GITHUB_APP_CLIENT_ID=[client-id]
export GITHUB_APP_CLIENT_SECRET=[client-secret]
export GITHUB_OAUTH_TOKEN=[token-here]

export SLACK_BOTUSER_OAUTH_TOKEN=[token-here]

export SENTRY_DSN=[sentry-dsn]
export DATADOG_API_KEY=[datadog-api-key]
```

Commits into `master` kick-off the build of the deployment docker image. Currently, an admin needs to ssh into the deployment box to manually trigger a refresh. Future iterations will investigate using container orchestration and/or the use of a development box for builds.

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
