# Contribution Guidelines

Busy Beaver welcomes any, and all, contributions. Every little bit helps!

#### Table of Contents

<!-- TOC -->

- [Architecture Overview](#architecture-overview)
  - [GitHub Activity Workflow](#github-activity-workflow)
- [Development Environment](#development-environment)
  - [Slack Integration](#slack-integration)
  - [Setting up Development Environment](#setting-up-development-environment)
  - [Verify Installation](#verify-installation)
  - [Running Tests](#running-tests)
- [Modifying Third-Party Integrations](#modifying-third-party-integrations)
- [Adding New Third-Party Integrations](#adding-new-third-party-integrations)
- [Miscellaneous](#miscellaneous)
  - [Pre-commit](#pre-commit)
  - [Slack Slash Commands](#slack-slash-commands)
  - [Task Queues](#task-queues)
  - [PDB++ Configuration](#pdb-configuration)

<!-- /TOC -->

## Architecture Overview

Busy Beaver is a Python application with a Slack frontend. The application consists of a set of REST endpoints with integrations to various services (GitHub, Slack, YouTube, Trello, etc) using public APIs / 3rd party libraries.

While the application is currently a monolith, it is built with Service-Oriented Architecture (SOA) in mind. API endpoints are implemented using Flask blueprints and services are integrated using the Adapter / Facade pattern.

Busy Beaver tasks are kicked off through `curl` requests scheduled via CRON.

### GitHub Activity Workflow

The following diagram shows a high-level workflow of the GitHub activity features:
<img src="assets/architecture.png" width=800 />

> When a Slack user chats "connect" to the bot user via direct message, the server receives the event details and generates a unique `state` identifier. The server logs the Slack user and identifier to our server database. The bot user chats a GitHub URL containing our GitHub app's `client_id` and the `state` identifier. The URL leads the user to a validation page in which they log in to GitHub and approve access to basic public information. Upon approval, the GitHub user's details and `state` identifier are sent to another server endpoint. The server updates the Slack user record with GitHub user details by using the `state` identifier as a common key.

#### GitHub Events

Busy Beaver currently supports the following GitHub public events:

- [CreateEvent](https://developer.github.com/v3/activity/events/types/#createevent) `ref_type` repository
- [ForkEvent](https://developer.github.com/v3/activity/events/types/#forkevent)
- [IssuesEvent](https://developer.github.com/v3/activity/events/types/#issuesevent) `action` opened
- [PublicEvent](https://developer.github.com/v3/activity/events/types/#publicevent)
- [PullRequestEvent](https://developer.github.com/v3/activity/events/types/#pullrequestevent) `action` opened
- [PushEvent](https://developer.github.com/v3/activity/events/types/#pushevent)
- [ReleaseEvent](https://developer.github.com/v3/activity/events/types/#releaseevent)
- [WatchEvent](https://developer.github.com/v3/activity/events/types/#watchevent) `action` started

## Development Environment

It is recommended that users create a personal **Slack Workspace** to use for bot development. This will allow for independent development without having to wait for project maintainers to grant access to the Busy Beaver development Slack.

### Slack Integration

<table><tr><td>
An in-depth guide can be followed at <a href=docs/development-create-slack-bot/readme.md> Create a Busy Beaver Slack Dev-Bot</a>
</td></tr></table></br>

1. [Create a Slack workspace](https://get.slack.help/hc/en-us/articles/206845317-Create-a-Slack-workspace)
1. [Create a Slack App](https://api.slack.com/apps) and set the **Development Slack Workspace** to the workspace from the previous step - [Create a Slack Dev-Bot - Init a Slack App](docs/development-create-slack-bot/readme.md#init-a-slack-app)
1. Configure the **Slack App** settings - [Create a Slack Dev-Bot - Slack App Settings](docs/development-create-slack-bot/readme.md#Slack-App-Settings)
1. Install **Slack App** to **Slack Workspace** - [Create a Slack Dev-Bot - Install App to Workspace](docs/development-create-slack-bot/readme.md#Install-App-to-Workspace)

### Setting up Development Environment

1. `pip install pre-commit`
1. Install [Git-LFS](https://git-lfs.github.com/)
1. Clone repo
1. `cd <directory of the git repo>`
1. `cp .env.template .env`
1. Define the following `.env` config values:

   |Key|Source Value|Details|
   |---|---|---|
   |**SLACK_BOTUSER_OAUTH_TOKEN**|From the Dev-Bot Slack App API page under `Install App > OAuth Tokens for Your Team > Bot User OAuth Access Token`| Value obtained after - [Create a Slack Dev-Bot - Define App OAuth and Permissions](docs/development-create-slack-bot/readme.md#Define-App-OAuth-and-Permissions)|
   |**SLACK_SIGNING_SECRET**|From the Dev-Bot Slack App API page under `Basic Information > App Credentials > Signing Secret`| Value obtained after - [Create a Slack Dev-Bot - Define App OAuth and Permissions](docs/development-create-slack-bot/readme.md#Define-App-OAuth-and-Permissions)|
   |**NGROK_BASE_URI**|From the **ngrok** instance forwarding address|Value obtained after - [Create a Slack Dev-Bot - Enable Event Subscription](docs/development-create-slack-bot/readme.md#Enable-Event-Subscription)|

   Note: The **NGROK_BASE_URI** and **Slack Event Subscription > Request URL** values may need to be updated each time a new **ngrok** instance is created or if the address is expired.

1. `make up` to refresh environment variables inside of Busy Beaver

### Verify Installation

1. `make dev-shell`
1. Try sending a message to a channel for the development **Slack Workspace** with the command:

   ```python
   # Make sure the the channel for example "test" exists!
   slack.post_message("This is a test message", channel="test")`
   ```

1. Check **#test** channel in your **Slack Workspace** to see if the message was posted

### Running Tests

To run the test suite,
first,
bring up the service.
Busy Beaver tests depend on a running database
and other pieces
so the following Makefile target will start Docker Compose
and get the required software going.

```bash
$ make up
```

Once Docker Compose is running,
run pytest with:

```bash
$ make test
```

## Modifying Third-Party Integrations

As each integration requires API credentials, it is recommended that contributors create apps for integration connect to their personal accounts.

## Adding New Third-Party Integrations

Provide detailed instructions on how to set up the integration so we can roll the feature out to the production instance of Busy Beaver with correct credentials.

## Miscellaneous

### Pre-commit

[Pre-commit](https://pre-commit.com/) is a tool used to enforce linting with `flake8` and code formatting with `black`. To get started using
pre-commit, `pip install pre-commit==1.14.4` (this is in the `requirements.txt` file). Then run `pre-commit install`
to install the `flake8` and `black` environments locally.

Pre-commit will run on files staged for change automatically. You can also check pre-commit hook compliance on staged
files by running `pre-commit run` at any time. Note that pre-commit ignores files that are not staged for change.

### Slack Slash Commands

Users are able to interact with Busy Beaver using the `/busybeaver [command]` interface provided through the Slack UI. All slash commands are routed to a Busy Beaver endpoint that was enabled earlier via the Slack Slash Command webhook.

Busy Beaver uses the [dictionary dispatch pattern](https://alysivji.github.io/quick-hit-dictionary-dispatch.html) to run command-specific logic. We leverage a `EventEmitter` class, inspired by the [node.js EventEmitter](https://nodejs.org/api/events.html#events_class_eventemitter), to allow for the creation of new slash commands with a simple decorator interface.

You can create a custom slash command, i.e. `/busybeaver news`, as follows:

```python
@slash_command_dispatcher.on("news")
def fetch_news(**data):
    # business logic to handle command goes here
```

- [Slack Docs: Slash Commands](https://api.slack.com/slash-commands)

### Task Queues

Busy Beaver uses [RQ](http://python-rq.org) to queue jobs and process them in the background with workers. [Redis](https://redis.io/) is used as the message broker in this asynchronous architecture.

The Docker Compose development environment spins up a single worker along with a Redis instance. For testing purposes, we set `is_async=False` to force code to be executed synchronously. Need to find a way to simulate production environment with workers in Travis, or it might make sense to migrate to Jenkins.

#### Creating a New Task

1. Create a SQLAlchemy model to store task-specific information to the database
1. Run a database migration, `$ make migration m="migration message"`
1. Create two functions: background job function (decorated with `@rq.job`) and trigger function to start background job
1. In the trigger function, start the background job and save job specific information to the database
1. Write tests unti you have confidence that your code works and can be reviewed by others

#### Notes

- The [Flask-RQ](https://flask-rq2.readthedocs.io/en/latest/) library provides convenient, Flask-specific helpers. Background tasks are identified using the `@rq.job` decorator; jobs can be created using the `[background_task_function_name].queue(params)` method.
- Both the trigger function and background task are unit tested to ensure things occur as expected. A high-level integration test can help codify the requirements of the workflow.
- Currently the workers listen on the `default` and `failed` queues. No particular reason, but haven't had the needed to use other queues.

### PDB++ Configuration

[PDB++](https://pypi.org/project/pdbpp/) improves the debugging experience inside the shell. Create a `.pdbrc.py` file inside of the root project folder.

```python
# ./.pdbrc.py

import pdb


class Config(pdb.DefaultConfig):
    sticky_by_default = True  # start in sticky mode
    current_line_color = 40  # black
```
