#!/usr/bin/env bash

set -euo pipefail

TENANTS=()
for tenant in $(yq '.tenants.[]' tenants.yaml); do
    TENANTS+=("$tenant")
done

printf -v joined "'%s'," "${TENANTS[@]}"
echo "[${joined%,}]"
popd &> /dev/null