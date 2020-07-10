# Redis Deployment

This file contains information about our Redis deployment.

## Notes

- helm command with values file
- [ ] do a helm template to make sure config is what we expect
- [ ] roll out redis in staging before production
- [ ] add scheduler deployment

- https://github.com/bitnami/charts/tree/master/bitnami/redis

### Staging

```console
helm repo add bitnami https://charts.bitnami.com/bitnami
helm search repo redis
helm install bb-queue-staging bitnami/redis -f kubernetes/helm/values__redis.yaml

kubectl apply -f kubernetes/service--bbqueue-staging.yaml
```

### Production

```console
helm install bb-queue-production  bitnami/redis -f kubernetes/helm/values__redis.yaml

kubectl apply -f kubernetes/service--bbqueue-production.yaml
```
