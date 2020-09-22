# DigitalOcean Deployment

Details about infrastructure set up on DigitalOcean.

#### Table of Contents

<!-- TOC -->

- [Kubernetes](#kubernetes)
  - [Prerequestites](#prerequestites)
  - [Setting up Staging Environment](#setting-up-staging-environment)
  - [Setting up Production Environment](#setting-up-production-environment)
  - [Secrets](#secrets)

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

### Secrets

Secrets are loaded from AWS Secrets Manager into Kuberenetes using Terraform.
