# Deployment

Material related to deploying Busy Beaver.

## Current Deployment Workflow

Busy Beaver is deployed as a Helm chart.
Currently we are manually running tasks and installing software,
will automate this with Ansible
as we get more familiar with Kubernetes and Helm.

### Prerequestites

The code for this is in my private Cloud Configuration repo.

- Install Helm
- Use Helm to set up `nginx`, `cert-manager`, `redis` (staging and prod), `fluent-bit`
- Add `busybeaver-staging` Secret to cluster
- Add `busybeaver-production` Secret to cluster

### Setting up Staging Environment

```console
helm install busybeaver-staging ./busybeaver/ -f values/staging.yaml
helm upgrade busybeaver-staging ./busybeaver/ -f values/staging.yaml --set image.version=[version]
```

### Setting up Production Environment

```console
helm install busybeaver-production ./busybeaver/ -f values/production.yaml
helm upgrade busybeaver-production ./busybeaver/ -f values/production.yaml --set image.version=[version]
```

### Deployment Notes

#### Developer Documentation

- Production URL: `https://app.busybeaverbot.com`
- Staging URL: `https://staging.busybeaverbot.com`
- if staging database gets deleted and we have to start again
  - will need to set up app for distribution and install it via OAuth
- Need to find a place to store information about accounts and credentials
  - KMS?

#### Secrets Format

All data values need to be `base64` encoded.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: busybeaver-[staging|production]
type: Opaque
data:
  db-uri:
  cache-uri:
  sentry-dsn:
  secret-key:
  slack-client-id:
  slack-client-secret:
  slack-botuser-oauth-token:
  slack-signing-secret:
  meetup-api-key:
  github-client-id:
  github-client-secret:
  github-oauth-token:
  github-signing-secret:
  twitter-access-token-secret:
  twitter-access-token:
  twitter-consumer-key:
  twitter-consumer-secret:
```

### Integration Checklist

#### Slack

For both staging and production apps

- [ ] Update URL in App Home Screen
- [ ] Name Bot: `Busy Beaver` with the username `@busybeaver`
- [ ] Slash Command: Enable `/busybeaver` and set up URL
- [ ] Update app permission
  - [ ] NEED TO DOCUMENT ALL OF THIS SOMEWHERE
- [ ] Update Auth Callback URL for installation
- [ ] Set up event subscriptions and put them to the URL
  - [ ] WHAT EVENT SUBSCRIPTIONS DO WE NEED TO ENABLE

#### GitHub

For both staging and production apps in the `busy-beaver-dev` organization

- [ ] update the callback URL

#### Twitter

For both staging and production app

- [ ] fetch application credentials and make into environment variables

#### Meetup

Currently using an API token generated
by an application in my personal account
for both staging and production.

#### Sentry

Have a `busybeaverbot` Project with 2 environments:
- `staging`
- `production`

#### Slack Requirements

- Workspace needs Twitter integration to expand Tweets
