# Contribution Guidelines

Busy-Beaver welcomes any, and all, contributions. Every little bit helps!

## Architecture Overview

Busy-Beaver is a Python application with a Slack frontend. The application consists of a set of REST endpoints with integrations to various services (GitHub, Slack, YouTube, Trello, etc) using public APIs / 3rd party libraries.

While the application is currently a monolith, it is built with Service-Oriented Architecture (SOA) in mind. API endpoints are implemented using Flask blueprints and services are integrated using the Adapter / Facade pattern.

Busy-Beaver tasks are kicked off through `curl` requests scheduled via CRON.

### GitHub Activity Workflow

The following diagram shows a high-level workflow of the GitHub activity features:
<img src="assets/architecture.png" width=800 />

## Development Environment

It is recommended that users create a personal Slack workspace to use for bot development. This will allow for independent development without having to wait for project maintainers to grant access to the Busy-Beaver development Slack.

### Slack Integration

1. [Create a Slack workspace](https://get.slack.help/hc/en-us/articles/206845317-Create-a-Slack-workspace)
1. [Create a Slack App](https://api.slack.com/apps) and set the development workspace to the workspace from the previous step
1. Configure Slack app settings (defined below)
1. Install application in workspace
1. Locate the `Bot User OAuth Access Token`, we will need that later on

#### Slack Settings

- Add a bot user
- Set Permission Scopes
  - `channels:read`
  - `chat:write:bot`
  - `bot`
  - `usergroups:read`
- Enable Event Subscription
  - callback URL: generate via `ngrok`, see below
  - Subscribe to bot events
    - message.im

### Setting up Development Environment

1. Clone repo
1. `cp .env.template .env`
1. Populate `SLACK_BOTUSER_OAUTH_TOKEN` field with value obtained in previous section
1. `make up`

## Modifying an Integration

As each integration requires API credentials, it is recommended that users create apps for integration in their account.

## Adding an Integration

Provide detailed instructions on how to set up the integration so we can roll the feature out to the production instance of Busy-Beaver with correct credentials.

Might be a good idea to set up a Busy-Bevaer email for project admins to deal with user accounts.
