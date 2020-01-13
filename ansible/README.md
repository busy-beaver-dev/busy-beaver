# Busy Beaver Ansible Playbooks

This folder contains Ansible configuration settings to deploy Busy Beaver on a VPS.

## `~/.bash_profile`

```bash
export POSTGRES_USER=[do-console]
export POSTGRES_PASSWORD=[do-console]
export POSTGRES_HOST=[do-console--public]
export POSTGRES_PORT=[do-console]
export POSTGRES_DATABASE=[do-console]
export DATABASE_URI=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DATABASE}?sslmode=require
export REDIS_URI=redis://redis:6379

export SECRET_KEY=[secret-key]

# clients
export BUSY_BEAVER_API_TOKEN=[bb-api-token]

export GITHUB_APP_CLIENT_ID=[client-id]
export GITHUB_APP_CLIENT_SECRET=[client-secret]
export GITHUB_OAUTH_TOKEN=[token-here]
export GITHUB_SIGNING_SECRET=[signing-secret]

export MEETUP_API_KEY=[meetup-api-key]

export SLACK_CLIENT_ID=[client-id]
export SLACK_CLIENT_SECRET=[client-secret]
export SLACK_BOTUSER_OAUTH_TOKEN=[token-here]
export SLACK_SIGNING_SECRET=[signing-secret]

export TWITTER_CONSUMER_KEY=[]
export TWITTER_CONSUMER_SECRET=[]
export TWITTER_ACCESS_TOKEN=[]
export TWITTER_ACCESS_TOKEN_SECRET=[]

export YOUTUBE_API_KEY=[]
export YOUTUBE_CHANNEL=[]

export BUSYBEAVER_SENTRY_DSN=[sentry-dsn]
export BUSYBEAVER_LOGGLY_TOKEN=[api-key]
```

## Deployment Workflow

1. Set environment variables in Ansible control environment: `HEALTHCHECK_GITHUB_SUMMARY_CHIPY`, `HEALTHCHECK_GITHUB_SUMMARY_BELGRADE`, `HEALTHCHECK_TWITTER_POLLER`, `HEALTHCHECK_SYNC_EVENTS_DATABASE`, `HEALTHCHECK_POST_UPCOMING_EVENTS`; grab uuid values from healthchecks.io
1. `pip install ansible` installed the machine you will be deploying from
1. Check to see what the ansible playbook would do, we can run `ansible-playbook -i ./hosts site.yml --ask-sudo-pass -C`
1. Remove `-C` option to run playbook to deploy app
