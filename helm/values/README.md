# Helm Values Files

[Values files](https://helm.sh/docs/chart_template_guide/values_files/) allow us to cusomtize Helm charts.

## Contents

|Filename|Description|
|---|---|
|`bb_production.yaml`|Production file for Busy Beaver chart|
|`bb_staging.yaml`|Staging file for Busy Beaver chart|
|`redis.yaml`|Values for [bitnmai/redis](https://github.com/bitnami/charts/tree/master/bitnami/redis)|

## Commands

### Redis

We will need to install Redis and copy the service DNS into the `bb_[environment].yaml`

```console
helm repo add bitnami https://charts.bitnami.com/bitnami

helm upgrade --install bb-queue-staging bitnami/redis -f ./helm/values/redis.yaml --namespace busybeaver-staging

helm upgrade  --install bb-queue-production bitnami/redis -f ./helm/values/redis.yaml --namespace busybeaver-production
```

### Busy Beaver App

The staging environment is brought up as needed.

```console
helm upgrade --install busybeaver-staging ./helm/charts/busybeaver/ -f ./helm/values/bb_staging.yaml --namespace busybeaver-staging --set image.version=[version]

helm upgrade  --install busybeaver-production ./helm/charts/busybeaver/ -f ./helm/values/bb_production.yaml --namespace busybeaver-production --set image.version=[version]
```
