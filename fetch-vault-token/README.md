# Fetch Vault Token

An action that enables a grabbing a vault token via a role and secret.

## Usage

```yaml
name: Test Fetch Vault Token

jobs:
  ff-merge:
    runs-on: ubuntu-latest
    steps:
      - name: Get Vault Token
        id: vault
        uses: ndustrialio/actions/fetch-vault-token@main
        with:
          vault-address: ${{ secrets.VAULT_ADDR }}
          secret-id: ${{ secrets.VAULT_SECRET_ID }}
          role-id: ${{ secrets.VAULT_ROLE_ID }}
      - name: Echo vault token
         run: |
          echo "token=${{ steps.vault.outputs.vault-token }}"
```