# Contribution Guidelines

Busy Beaver welcomes any, and all, contributions. Every little bit helps!

#### Table of Contents

<!-- TOC -->

- [Architecture Overview](#architecture-overview)
  - [Application Stack](#application-stack)
  - [Deployment](#deployment)
  - [Services](#services)
- [Development Environment](#development-environment)
  - [Slack Integration](#slack-integration)
  - [Setting up Development Environment](#setting-up-development-environment)
  - [Verify Installation](#verify-installation)
  - [Running Tests](#running-tests)
- [Developer Documentation](#developer-documentation)
  - [Adding New Requirements](#adding-new-requirements)
  - [Modifying Third-Party Integrations](#modifying-third-party-integrations)
  - [Adding New Third-Party Integrations](#adding-new-third-party-integrations)
  - [Creating new CLI Command](#creating-new-cli-command)
- [Slack Slash Commands](#slack-slash-commands)
- [Task Queues](#task-queues)
  - [Creating a New Task](#creating-a-new-task)
  - [Notes](#notes)
- [Miscellaneous](#miscellaneous)
  - [Pre-commit](#pre-commit)
  - [PDB++ Configuration](#pdb-configuration)
  - [Windows Development](#windows-development)
  - [Pushing Commits to Pull Request made from Fork](#pushing-commits-to-pull-request-made-from-fork)

<!-- /TOC -->

## Architecture Overview

Busy Beaver is a Python application with a Slack frontend. The application consists of a set of REST endpoints with integrations to various services (GitHub, Slack, YouTube, Trello, etc) using public APIs / 3rd party libraries.

While the application is currently a monolith, it is built with Service-Oriented Architecture (SOA) in mind. API endpoints are implemented using Flask blueprints and services are integrated using the Adapter / Facade pattern.

Busy Beaver tasks are kicked off via CRON jobs that schedule tasks to be run on async workers.

### Application Stack

- [PostgreSQL](https://www.postgresql.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Flask](http://flask.pocoo.org/)
- [flask-sqlalchemy](http://flask-sqlalchemy.pocoo.org/)
- [flask-migrate](https://flask-migrate.readthedocs.io/en/latest/)
- [requests](https://github.com/requests/requests)

#### Tests

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

[Prerequisites for developing on Windows](#windows-development)

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
   |**SLACK_DEV_WORKSPACE_ID**|From Browser Console; follow [instructions from StackOverflow](https://stackoverflow.com/a/44883343/4326704)
   |**SLACK_DEV_WORKSPACE_CHANNEL_ID**|Channel to install integration into (Need to join a channel). How to get this?

1. `make up` to refresh environment variables inside of Busy Beaver

### Verify Installation

1. `make flaskshell`
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

## Developer Documentation

### Adding New Requirements

Busy Beaver uses [`pip-tools`](https://github.com/jazzband/pip-tools) to
manage `pip` dependencies.

If you need to update any mainline dependencies in `requirements.txt`,
please add the package to `requirements.in` and
run the following command:
`pip-compile --output-file=requirements.txt requirements.in`.

You will need to have `pip-tools` installed on your local machine to
perform this actin.

### Modifying Third-Party Integrations

As each integration requires API credentials, it is recommended that contributors create apps for integration connect to their personal accounts.

### Adding New Third-Party Integrations

Provide detailed instructions on how to set up the integration so we can roll the feature out to the production instance of Busy Beaver with correct credentials.

### Creating new CLI Command

Create a `cli.py` module. Place this in your application folder next to `blueprint.py`.

```python
# cli.py

import logging

import click

from .blueprint import bp

logger = logging.getLogger(__name__)


@click.option("--workspace", required=True)
@bp.cli.command("function_name", help="Help prompt")
def function_name(*args, **kwargs)):
    pass
```

## Slack Slash Commands

Users are able to interact with Busy Beaver using the `/busybeaver [command]` interface provided through the Slack UI. All slash commands are routed to a Busy Beaver endpoint that was enabled earlier via the Slack Slash Command webhook.

Busy Beaver uses the [dictionary dispatch pattern](https://alysivji.github.io/quick-hit-dictionary-dispatch.html) to run command-specific logic. We leverage a `EventEmitter` class, inspired by the [node.js EventEmitter](https://nodejs.org/api/events.html#events_class_eventemitter), to allow for the creation of new slash commands with a simple decorator interface.

You can create a custom slash command, i.e. `/busybeaver news`, as follows:

```python
@slash_command_dispatcher.on("news")
def fetch_news(**data):
    # business logic to handle command goes here
```

- [Slack Docs: Slash Commands](https://api.slack.com/slash-commands)

## Task Queues

Busy Beaver uses [RQ](http://python-rq.org) to queue jobs and process them in the background with workers. [Redis](https://redis.io/) is used as the message broker in this asynchronous architecture.

The Docker Compose development environment spins up a single worker along with a Redis instance. For testing purposes, we set `is_async=False` to force code to be executed synchronously. Need to find a way to simulate production environment with workers in Travis, or it might make sense to migrate to Jenkins.

### Creating a New Task

1. Create a SQLAlchemy model to store task-specific information to the database
1. Run a database migration, `$ make migration m="migration message"`
1. Create two functions: background job function (decorated with `@rq.job`) and trigger function to start background job
1. In the trigger function, start the background job and save job specific information to the database
1. Write tests unti you have confidence that your code works and can be reviewed by others

### Notes

- The [Flask-RQ](https://flask-rq2.readthedocs.io/en/latest/) library provides convenient, Flask-specific helpers. Background tasks are identified using the `@rq.job` decorator; jobs can be created using the `[background_task_function_name].queue(params)` method.
- Both the trigger function and background task are unit tested to ensure things occur as expected. A high-level integration test can help codify the requirements of the workflow.
- Currently the workers listen on the `default` and `failed` queues. No particular reason, but haven't had the needed to use other queues.

## Miscellaneous

### Pre-commit

[Pre-commit](https://pre-commit.com/) is a tool used to enforce linting with `flake8` and code formatting with `black`. To get started using
pre-commit, `pip install pre-commit==1.14.4` (this is in the `requirements.txt` file). Then run `pre-commit install`
to install the `flake8` and `black` environments locally.

Pre-commit will run on files staged for change automatically. You can also check pre-commit hook compliance on staged
files by running `pre-commit run` at any time. Note that pre-commit ignores files that are not staged for change.

### PDB++ Configuration

[PDB++](https://pypi.org/project/pdbpp/) improves the debugging experience inside the shell. Create a `.pdbrc.py` file inside of the root project folder.

```python
# ./.pdbrc.py

import pdb


class Config(pdb.DefaultConfig):
    sticky_by_default = True  # start in sticky mode
    current_line_color = 40  # black
```

### Windows Development

#### Windows Prerequisites

1. Configure Git on Windows to properly handle line endings

```bash
git config --global core.autocrlf input
git config --global core.eol lf
```

1. Install [Windows Sub-System for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
1. Install [Docker on WSL](https://nickjanetakis.com/blog/setting-up-docker-for-windows-and-wsl-to-work-flawlessly)
1. Configure Docker for Windows:
    - Expose daemon on tcp://localhost without TLS
    - Add Shared Drive<br />
    <img src="docs/diagrams/docker-windows-expose.png" alt="Docker" width=300 /><br />
    <img src="docs/diagrams/docker-windows-shared.png" alt="Docker" width=300 />
1. [Proceed with Setting up Development Environment](#setting-up-development-environment)

#### Windows Troubleshooting

If run into issues with `make up`, it's most likely Windows and Docker. Try the following:

1. Restart Computer
1. Set File Permissions & Fix Line Endings
1. Launch WSL
1. Navigate to busy-beaver root directory and run following:
    ```bash
    sudo apt-get install dos2unix
    sudo dos2unix scripts/entrypoint.sh
    sudo chmod +x scripts/entrypoint.sh
    docker-compose build --no-cache
    make up
    ```
1. Docker >>> Settings >> Shared Drives:
    - Uncheck any Shared drive, Click Apply
    - Check Shared Drives, Click Apply
1. Docker >>> Settings >> Reset
    - Reset to factory defaults...
1. Uninstall Windows, Install Linux

### Pushing Commits to Pull Request made from Fork

GitHub allows upstream maintainers, with permission,
to push to downstream forks.

We are using [Git-LFS](https://git-lfs.github.com/) to keep binary files
out of our Git tree.
Unfortunately LFS makes it a bit tricky to
push to downstream forks out of the box,
see [issue](https://github.com/git-lfs/git-lfs/issues/2291).

To push to downstream forks,
you will need to `rm .git/hooks/pre-push`.
It is recommended that you move the file somewhere else
before making the change.
Replace the file once you are done.

#### Additional Resources

- [Pushing to someone else's pull request on GitHub](https://jonathanchang.org/blog/pushing-to-a-pull-request-on-github/)
- [Git-LFS Issue -- Authentication required : You must have push access to verify locks error](https://github.com/git-lfs/git-lfs/issues/2291)
