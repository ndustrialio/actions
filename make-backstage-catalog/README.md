# Convert meta.yaml to Backstage catalog-info.yaml

An action that takes your repository's meta.yaml and outputs + commits a Backstage compatible catalog-info.yaml to the root directory of your repo

Should be used in a workflow that triggers on an update to the meta.yaml

## Usage

```yaml
name: Generate Backstage catalog-info

on:
  push:
    branches: [main]
    paths: 
      - 'meta.yaml'
  pull_request:
    branches: [main]
    paths: 
      - 'meta.yaml'
jobs:
  create-backstage-config:
    runs-on: ubuntu-latest
    steps:
    - name: Generate Backstage catalog config from meta.yaml
      id: makecatalog
      uses: ndustrialio/ndustrial-actions/make-backstage-catalog@master
```