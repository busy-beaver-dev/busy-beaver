# Contribution Guidelines

Busy-Beaver welcomes any, and all, contributions. Every little bit helps!

## Architecture Overview

Busy-Beaver is a Python application with a Slack frontend. The application consists of a set of REST endpoints with integrations to various services (GitHub, Slack, YouTube, Trello, etc) using public APIs / 3rd party libraries.

While the application is currently a monolith, it is built with Service-Oriented Architecture (SOA) in mind. API endpoints are implemented using Flask blueprints and services are integrated using the Adapter / Facade pattern.

Busy-Beaver tasks are kicked off through `curl` requests scheduled via CRON.

### GitHub Activity Workflow

The following diagram shows a high-level workflow of the GitHub activity features:
<img src="assets/architecture.png" width=800 />

> When a Slack user chats "connect" to the bot user via direct message, the server receives the event details and generates a unique `state` identifier. The server logs the Slack user and identifier to our server database. The bot user chats a GitHub URL containing our GitHub app's `client_id` and the `state` identifier. The URL leads the user to a validation page in which they log in to GitHub and approve access to basic public information. Upon approval, the GitHub user's details and `state` identifier are sent to another server endpoint. The server updates the Slack user record with GitHub user details by using the `state` identifier as a common key.

## Development Environment

It is recommended that users create a personal **Slack Workspace** to use for bot development. This will allow for independent development without having to wait for project maintainers to grant access to the Busy-Beaver development Slack.

### Slack Integration

<table><tr><td>
An in-depth guide can be followed at <a href=docs/development-create-slack-bot/readme.md> Create a Busy-Beaver Slack Dev-Bot</a>
</td></tr></table></br>

1. [Create a Slack workspace](https://get.slack.help/hc/en-us/articles/206845317-Create-a-Slack-workspace)
1. [Create a Slack App](https://api.slack.com/apps) and set the **Development Slack Workspace** to the workspace from the previous step - [Create a Slack Dev-Bot - Init a Slack App](doc/development-create-slack-bot/readme.md#init-a-slack-app)
1. Configure the **Slack App** settings - [Create a Slack Dev-Bot - Slack App Settings](doc/development-create-slack-bot/readme.md#Slack-App-Settings)
1. Install **Slack App** to **Slack Workspace** - [Create a Slack Dev-Bot - Install App to Workspace](doc/development-create-slack-bot/readme.md#Install-App-to-Workspace)

### Setting up Development Environment

1. `pip install pre-commit`
1. `make
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

1. `make up` to refresh environment variables inside of Busy-Beaver

### Verify Installation

1. `make dev-shell`
1. Try sending a message to a channel for the development **Slack Workspace** with the command:

   ```python
   # Make sure the the channel for example "test" exists!
   slack.post_message("This is a test message", channel="test")`
   ```

1. Check **#test** channel in your **Slack Workspace** to see if the message was posted

## Modifying Integration

As each integration requires API credentials, it is recommended that contributors create apps for integration connect to their personal accounts.

## Adding New Integration

Provide detailed instructions on how to set up the integration so we can roll the feature out to the production instance of Busy-Beaver with correct credentials.

## Notes

### [pdb++](https://pypi.org/project/pdbpp/) Configuration

PDB++ improves the debugging experience inside the shell. Create a `.pdbrc.py` file inside of the root project folder.

```python
# ./.pdbrc.py

import pdb


class Config(pdb.DefaultConfig):
    sticky_by_default = True  # start in sticky mode
    current_line_color = 40  # black
```

### [pre-commit](https://pre-commit.com/)

Pre-commit is a tool used to enforce linting with `flake8` and code formatting with `black`. To get started using
pre-commit, `pip install pre-commit==1.14.4` (this is in the `requirements.txt` file). Then run `pre-commit install`
to install the `flake8` and `black` environments locally.

Pre-commit will run on files staged for change automatically. You can also check pre-commit hook compliance on staged
files by running `pre-commit run` at any time. Note that pre-commit ignores files that are not staged for change.
