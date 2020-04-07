# Deployment

Material related to deploying Busy Beaver.

## Current Deployment Workflow

Busy Beaver has been packaged up as a Helm chart.

### Instructions

- Ensure `busybeaver-staging` secrets exists

```console
helm install bb-staging ./busybeaver/
helm upgrade bb-staging ./busybeaver/
```
