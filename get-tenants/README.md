# Return the list of tenants

An action that enables a grabbing a list of current tenants.

## Usage

```yaml
name: Test tenants

on:
  push:
    branches: [tenantsJob]

jobs:
  get-tenants:
    runs-on: ubuntu-latest
    outputs:
      tenants: ${{ steps.gts.outputs.tenants }}
    steps:
      - name: Get Tenants
        uses: ndustrialio/actions/get-tenants@tenantsJob
        id: gts
  run-tenant:
    runs-on: ubuntu-latest
    needs: [get-tenants]
    strategy:
      matrix:
        TENANT: ${{fromJSON(needs.get-tenants.outputs.tenants)}}
    steps:
      - uses: actions/checkout@v2
      - name: Set environment
        run: |
          echo ${{ matrix.TENANT }}
```