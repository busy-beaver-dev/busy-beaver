# Helm Values Files

[Values files](https://helm.sh/docs/chart_template_guide/values_files/) allow us to cusomtize Helm charts.

## Contents

|Filename|Description|
|---|---|
|production.yaml|Production file for Busy Beaver chart|
|staging.yaml|Staging file for Busy Beaver chart|

## Commands

### Busy Beaver App

```console
helm upgrade busybeaver-production ./helm/charts/busybeaver/ -f ./helm/values/production.yaml --set image.version=[version]

helm upgrade busybeaver-staging ./helm/charts/busybeaver/ -f ./helm/values/staging.yaml --set image.version=[version]
```

### Redis

```console
```
