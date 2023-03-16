#!/usr/bin/env bash

set -euo pipefail

DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
pushd "$DIR" &> /dev/null
TENANTS=()
for tenant in $(yq '.tenants.[]' tenants.yaml); do
    TENANTS+=("$tenant")
done

printf -v joined "'%s'," "${TENANTS[@]}"
echo "[${joined%,}]"
popd &> /dev/null