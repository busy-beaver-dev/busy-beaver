# Helm Values Files

[Values files](https://helm.sh/docs/chart_template_guide/values_files/) allow us to cusomtize Helm charts.

## Contents

|Filename|Description|
|---|---|
|production.yaml|Production file for Busy Beaver chart|
|staging.yaml|Staging file for Busy Beaver chart|

## Commands

### Redis

We will need to install Redis and copy the service DNS into the `bb_[environment].yaml`

```console
helm repo add bitnami https://charts.bitnami.com/bitnami

helm install bb-queue-staging bitnami/redis -f ./helm/values/redis.yaml
```

### Busy Beaver App

The staging environment is brought up as needed.

```console
helm install busybeaver-production ./helm/charts/busybeaver/ -f ./helm/values/bb_production.yaml --set image.version=[version]

helm upgrade busybeaver-staging ./helm/charts/busybeaver/ -f ./helm/values/bb_staging.yaml --set image.version=[version]
```
