# DigitalOcean Deployment

Details about infrastructure set up on DigitalOcean.

#### Table of Contents

<!-- TOC -->

- [Kubernetes](#kubernetes)
  - [Prerequestites](#prerequestites)
  - [Setting up Staging Environment](#setting-up-staging-environment)
  - [Setting up Production Environment](#setting-up-production-environment)
  - [Deploying App](#deploying-app)
  - [Secrets Format](#secrets-format)

<!-- /TOC -->

## Kubernetes

Busy Beaver is deployed to Kubernets as a Helm chart.

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

### Secrets Format

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
