# Helm Upgrade

An action that performs a `helm upgrade`.

## Usage

```yaml
name: Deploy

on:
  push:
    branches: [main, staging]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        uses: ndustrialio/actions/helm-upgrade@main
        with:
          kubeconfig: ${{ secrets.KUBE_CONFIG }}
          namespace: your-namespace
          tag: latest
          env: prod
          chart: deployment
          chart-version: "0.1.30"
```
