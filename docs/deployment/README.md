# Deployment

Material related to deploying Busy Beaver.

#### Table of Contents

<!-- TOC -->

- [Stack](#stack)
  - [Deploying App](#deploying-app)
  - [Deployment Notes](#deployment-notes)
- [Integration Notes](#integration-notes)
  - [GitHub](#github)
  - [Twitter](#twitter)
  - [Meetup](#meetup)
  - [Sentry](#sentry)

<!-- /TOC -->

## Stack

- Deployment has been packaged up as a Helm chart
- Deployed out to DigitalOcean-managed Kubernete
- Database is DO-managed postgres
- see [DO deployment](digitalocean_deployment.md) for more details

### Deploying App

There is a GitHub workflow that can be triggered to deploy the BusyBeaver using `helm upgrade`. Hit https://api.github.com/repos/busy-beaver-dev/busy-beaver/deployments with a POST request:

- body: `{"ref": "VERSION"}`
- headers
  - `Authorization`: `Token {}`
  - `Accept`: `application/vnd.github.v3+json`

### Deployment Notes

- Production URL: `https://app.busybeaverbot.com`
- Staging URL: `https://staging.busybeaverbot.com`
- if staging database gets deleted and we have to start again
  - will need to set up app for distribution and install it via OAuth
- Need to find a place to store information about accounts and credentials
  - current in my personal account
  - KMS? LastPass?

## Integration Notes

- [Slack](notes/slack_integration.md)

### GitHub

For both staging and production apps in the `busy-beaver-dev` organization

- [ ] update the callback URL

### Twitter

For both staging and production app

- [ ] fetch application credentials and make into environment variables

### Meetup

Currently using an API token generated
by an application in my personal account
for both staging and production.

### Sentry

Have a `busybeaverbot` Project with 2 environments:

- `staging`
- `production`
