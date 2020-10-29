<p align="center"><img src="assets/logo.png" alt="Busy Beaver Logo" width=300 /></p>

# Busy Beaver

![build status](https://github.com/busy-beaver-dev/busy-beaver/workflows/build/badge.svg?branch=master&event=push)
[![codecov](https://codecov.io/gh/busy-beaver-dev/busy-beaver/branch/master/graph/badge.svg)](https://codecov.io/gh/busy-beaver-dev/busy-beaver)
[![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Chicago Python's Community Engagement Slack bot.

## Introduction

With over six thousand members, the [Chicago Python Users Group](https://www.chipy.org/) (ChiPy) is one of the largest Python communities in the world. Slack has become the primary method of communication amongst our members in-between events. We developed an open-source Slack bot, codename: Busy Beaver, to increase community engagement.

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

### Call For Proposals

Busy Beaver posts open Call For Proposals (CFP) for your organization and upcoming Python conferences in a designated channel.

Note: This feature is in beta. Please create an issue if you would like support for other conference types.

### Roadmap

We are currently working on additional features to improve ChiPy community engagement. Please join the conversation in `#busy-beaver-meta` on the [ChiPy Slack](https://chipy.slack.com/).

## Installing

<a href="https://slack.com/oauth/v2/authorize?response_type=code&client_id=795376369155.506256439575&redirect_uri=https%3A%2F%2Fapp.busybeaverbot.com%2Fslack%2Finstallation-callback&scope=app_mentions%3Aread+channels%3Ahistory+channels%3Ajoin+channels%3Aread+chat%3Awrite+commands+emoji%3Aread+groups%3Aread+im%3Ahistory+im%3Aread+im%3Awrite+mpim%3Ahistory+mpim%3Aread+mpim%3Awrite+reactions%3Aread+reactions%3Awrite+team%3Aread+usergroups%3Aread+users.profile%3Aread+users%3Aread+users%3Awrite&state=gRDlCeK5MLXQHsDOXYjaf44tbewwKt">
<img alt=""Add to Slack"" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" /></a>

## Contributing

Busy Beaver is always looking for new contributors! Previous open source experience is not required! Please see [CONTRIBUTING.md](CONTRIBUTING.md).
