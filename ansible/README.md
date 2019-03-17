# Busy Beaver Ansible Playbooks

This folder contains Ansible configuration settings to deploy Busy-Beaver on a VPS.

## `~/.bash_profile`

```bash
export POSTGRES_USER=[user]
export POSTGRES_PASSWORD=[password]
export DATABASE_URI=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/busy-beaver
export BUSY_BEAVER_API_TOKEN=[bb-api-token]

export GITHUB_APP_CLIENT_ID=[client-id]
export GITHUB_APP_CLIENT_SECRET=[client-secret]
export GITHUB_OAUTH_TOKEN=[token-here]

export SLACK_BOTUSER_OAUTH_TOKEN=[token-here]

export TWITTER_CONSUMER_KEY=[]
export TWITTER_CONSUMER_SECRET=[]
export TWITTER_ACCESS_TOKEN=[]
export TWITTER_ACCESS_TOKEN_SECRET=[]

export SENTRY_DSN=[sentry-dsn]
export DATADOG_API_KEY=[datadog-api-key]
```

## AWS Credentials

Create AWS credentials file, `/.aws/credentials`, using details in the [IAM Console](https://console.aws.amazon.com/iam/home)

```ini
[default]
aws_access_key_id = []
aws_secret_access_key = []
```

## Deployment Workflow

1. `pip install ansible` installed the machine you will be deploying from
2. Check to see what the ansible playbook would do, we can run `ansible-playbook -i ./hosts site.yml --ask-sudo-pass -C`
3. Remove `-C` option to run playbook to deploy app

## Reloading Database from Backup

[Postgres Docs](https://www.postgresql.org/docs/8.1/backup.html#BACKUP-DUMP-RESTORE)

```console
psql -U ${POSTGRES_USER} busy-beaver < [sql_dump]
```
