# Deployment

Material related to deploying Busy Beaver.

## Current Deployment Workflow

Busy Beaver has been packaged up as a Helm chart.

### Instructions

- Set up `cert-manager` and `nginx`
- Ensure `busybeaver-staging` secrets exists
  - TODO what is the format?

```console
helm install bb-staging ./busybeaver/
helm upgrade bb-staging ./busybeaver/
```
