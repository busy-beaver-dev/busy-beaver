# Busy Beaver

<p align="center"><img src="assets/logo.png" alt="Busy Beaver Logo" width=300 /></p>

![build status](https://github.com/busy-beaver-dev/busy-beaver/workflows/build/badge.svg?branch=master&event=push)
[![codecov](https://codecov.io/gh/busy-beaver-dev/busy-beaver/branch/master/graph/badge.svg)](https://codecov.io/gh/busy-beaver-dev/busy-beaver)
[![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Chicago Python's Community Engagement Slack bot.

## Introduction

With over four thousand members, the [Chicago Python Users Group](https://www.chipy.org/) (ChiPy) is one of the largest Python communities in the world. Slack has become the primary method of communication amongst our members in-between events. We developed an open-source Slack bot, codename: Busy Beaver, to increase community engagement.

We released Busy Beaver on Jan 10th, 2019 at the Chicago Python `__main__` Meeting. [Slides](http://bit.ly/busy-beaver) and [video recording](https://www.youtube.com/watch?v=7dBESR_x7Kc) from the release announcement are available online.

## Features

### Upcoming Events

Busy Beaver integrates with Meetup API to provide details about upcoming events. Events are downloaded to the Busy Beaver database periodically.

Users are able to query using the `/busybeaver` [slash command](https://api.slack.com/slash-commands).

- `/busybeaver next` shows details of the upcoming event
- `/busybeaver events` shows details of upcoming events

A periodic CRON job has been set to post the contents of `/busybeaver events` in a designed Slack channel.

### GitHub Activity

Busy Beaver posts daily summaries of public GitHub activity for registered users in the `#busy-beaver` channel on the [ChiPy Slack](https://chipy.slack.com/). The goal of this feature is to increase engagement by sparking conversations around GitHub activity.

Users sign up for an account by `DM`ing the bot with the phrase: `connect`. The bot requires users to sign into GitHub to ensure only authorized activity is posted in the channel.

### Retweeter

Busy Beaver retweets posts made to the [@ChicagoPython Twitter account](https://twitter.com/ChicagoPython) in the `#at-chicagopython` channel on the [ChiPy Slack](https://chipy.slack.com/).

## Roadmap

We are currently working on additional features to improve ChiPy community engagement. Please join the conversation in `#busy-beaver-meta` on the [ChiPy Slack](https://chipy.slack.com/).

## Contributing

Busy Beaver is always looking for new contributors! Previous open source experience is not required! Please see [CONTRIBUTING.md](CONTRIBUTING.md).

## Development Notes

Busy Beaver is an open source project where all artificats (code, Docker image, etc) are online. We use the [Twelve-Factor Application Methodology](https://12factor.net) for building services to design the CICD process and to keep information secure.

### Web Application Stack

- [PostgreSQL](https://www.postgresql.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Flask](http://flask.pocoo.org/)
- [flask-sqlalchemy](http://flask-sqlalchemy.pocoo.org/)
- [flask-migrate](https://flask-migrate.readthedocs.io/en/latest/)
- [requests](https://github.com/requests/requests)

### Tests

- [pytest](https://github.com/pytest-dev/pytest)
- [vcr.py](https://github.com/kevin1024/vcrpy)
- [pytest-vcr](https://github.com/ktosiek/pytest-vcr)
- [pytest-freezegun](https://github.com/ktosiek/pytest-freezegun)

`vcr.py` records cassettes of requests and responses for new tests, and replays them for previously written tests. Make sure to [filter credentials](https://vcrpy.readthedocs.io/en/latest/advanced.html#filter-information-from-http-headers)

### Deployment

- [Helm](https://helm.sh/)
- [Kubernetes](https://kubernetes.io/)
- [Docker](https://hub.docker.com/search/?type=edition&offering=community)
- [DigitalOcean](https://www.digitalocean.com)

### Services

We are grateful to the following organizations for providing free services to open source projects:

- [GitHub](https://github.com)
- [DockerHub](https://hub.docker.com)
