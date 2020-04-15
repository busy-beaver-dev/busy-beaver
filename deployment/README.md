# Deployment

Material related to deploying Busy Beaver.

## Current Deployment Workflow

Busy Beaver has been packaged up as a Helm chart.

### Prerequestites

- Install Helm
- Use Helm to set up `nginx`, `cert-manager`, `redis`, fluent-bit
- Add `busybeaver-staging` Secret to cluster

### Installing Busy Beaver -- Staging

```console
helm install busybeaver-staging ./busybeaver/ -f values/staging.yaml
helm upgrade busybeaver-staging ./busybeaver/ -f values/staging.yaml
```

### Installing Busy Beaver -- Production

```console
helm install busybeaver-production ./busybeaver/ -f values/production.yaml
helm upgrade busybeaver-production ./busybeaver/ -f values/production.yaml
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

### Notes

- if staging database gets deleted and we have to start again
  - will need to set up app for distribution and install it via OAuth
- TODO (need to clean this up)
  - [ ] what accounts did we need to create?
    - [ ] what are those accounts?
    - [ ] where do we store credentials?
