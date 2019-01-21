# Busy Beaver Ansible Playbooks

This folder contains Ansible configuration settings to deploy Busy-Beaver on a VPS.

## `~/.bash_profile`

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

## Deployment Workflow

1. `pip install ansible` installed the machine you will be deploying from
2. Check to see what the ansible playbook would do, we can run `ansible-playbook -i ./hosts playbook.yml -C`
3. Remove `-C` option to run playbook to deploy app
